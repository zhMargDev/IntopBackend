import firebase_admin
import uuid

from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from firebase_admin import auth, db, credentials, messaging
from firebase_admin.exceptions import FirebaseError

from firebase_conf import firebase
from database import get_db
from models.models import User, Role
from schemas.user import *
from utils.token import decode_access_token, update_token
from schemas.sms import *
from documentation.users import auth as authorization_documentation
from utils.user import get_current_user

router = APIRouter()

# Инициализация CryptContext для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    # Хеширование пароля
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    # Проверка 2х паролей с хешированием
    return pwd_context.verify(plain_password, hashed_password)



def send_verification_code(registration_token, code):
    message = messaging.Message(
        notification=messaging.Notification(
            title="Код подтверждения",
            body="Ваш код: " + code
        ),
        data={
            "code": code
        },
        token=registration_token
    )

    # Send a message to the device corresponding to the provided
    # registration token.
    response = messaging.send(message)  

    print('Successfully sent message:', response)
    
def send_verification_code(phone_number):
    verification_id = None
    try:
        verification_id = auth.generate_email_verification_link(phone_number)
        print(verification_id)
    except FirebaseError as e:
        print(e)
    return verification_id

def verify_phone_number(verification_id, verification_code):
    try:
        phone_auth = auth.PhoneAuthProvider.get_credential(verification_id, verification_code)
        user = auth.sign_in_with_credential(phone_auth)
        print('Пользователь успешно авторизован:', user.uid)
    except auth.exceptions.FirebaseAuthException as e:
        print(e)

@router.get('/test')
async def test():
    verification_id = send_verification_code('nj.dark.soul@gmail.com')
    return verification_id

@router.get("/protected")
async def protected_route(current_user: dict = Depends(get_current_user)):
    return {"message": "This is a protected route", "user": current_user}

@router.post("/register_with_email",
             summary="Регистрация через email.",
             description=authorization_documentation.register_with_phone_number_description)
async def register_with_email(data: User):
    try:
        # Создание нового пользователя в Firebase с флагом is_verified = false
        user = auth.create_user(
            email=data.email,
            password=data.password,
            email_verified=False
        )

        data.created_at = data.created_at.isoformat()
        data.last_active = data.last_active.isoformat()

        # Преобразование модели User в словарь для записи в Realtime Database
        user_data_dict = data.dict(exclude={"password"})  # Исключаем пароль из данных для записи
        user_data_dict["uid"] = user.uid

        # Сохранение всех данных в Realtime Database
        db.reference("users").child(user.uid).set(user_data_dict)


        # Получение экземпляра аутентификации
        py_auth = firebase.auth()

        # Выполнение входа пользователя для получения токена
        user_credentials = py_auth.sign_in_with_email_and_password(data.email, data.password)
        id_token = user_credentials['idToken']

        # Отправка письма с кодом подтверждения
        try:
            py_auth.send_email_verification(id_token)
            print("Письмо с кодом подтверждения отправлено на", data.email)
        except Exception as e:
            print("Ошибка при отправке письма:", str(e))

        # Возврат сообщения об успешной регистрации
        return {"message": "Пользователь успешно зарегистрирован. Пожалуйста, проверьте вашу почту для подтверждения."}
    except FirebaseError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/register_with_phone",
             summary="Регистрация через номер телефона.",
             description=authorization_documentation.register_with_email_description)
async def register_with_phone(data: User):
    try:
        # Создание пользователя в Firebase с использованием номера телефона
        user = auth.create_user(
            phone_number=data.phone_number,
            password=data.password,
            email_verified=False
        )

        data.created_at = data.created_at.isoformat()
        data.last_active = data.last_active.isoformat()

        # Преобразование модели User в словарь для записи в Realtime Database
        user_data_dict = data.dict(exclude={"password"})  # Исключаем пароль из данных для записи
        user_data_dict["uid"] = user.uid


        # Генерация кода подтверждения и отправка SMS
        #verification_id = auth.generate_verification_id(phone_number=data.phone_number)
        # Сохранение всех данных в Realtime Database
        db.reference("users").child(user.uid).set(user_data_dict)

        # Возврат сообщения об успешной регистрации
        return {"message": "Код подтверждения отправлен на ваш номер телефона. Проверьте SMS."}
    except FirebaseError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login_with_email", 
             summary="Вход через email.",
             description=authorization_documentation.login_with_email_description)
async def login_with_email(data: EmailRegistration):
    try:
        # Получение пользователя по email
        user = auth.get_user_by_email(data.email)
        # Здесь можно добавить логику для проверки пароля (обычно это делается на клиенте)
        if not user.email_verified:
            raise HTTPException(status_code=403, detail="Пользователь не верифицирован. Пожалуйста, проверьте вашу почту для подтверждения.")
        return {"message": "Пользователь авторизован.", "user_id": user.uid}
    except FirebaseError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login_with_phone_number", 
             summary="Вход через email.",
             description=authorization_documentation.login_with_phone_number_description)
async def login_with_phone_number(data: PhoneVerification):
    try:
        # Получение пользователя по email
        user = auth.get_user_by_phone_number(data.phone_number)
        # Здесь можно добавить логику для проверки пароля (обычно это делается на клиенте)
        return {"message": "Пользователь авторизован.", "user_id": user.uid}
    except FirebaseError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Телеграм авторизация
@router.post("/tg_authorization", 
             summary="Авторизация через Telegram",
             description=authorization_documentation.tg_authorization)
async def tg_authorization(init_data: TelegramInitData, db: Session = Depends(get_db)):
    # Поиск пользователя по Telegram ID
    user = db.query(User).filter(User.telegram_id == str(init_data.id)).first()
    
    if user:
        # Обновление информации о существующем пользователе
        user.first_name = init_data.first_name
        user.second_name = init_data.last_name
        user.username = init_data.username
        user.last_active = datetime.now()  # Обновляем время последнего действия

        # Проверка и обновление состояния is_active
        if not user.is_active:
            user.is_active = True

        db.commit()
        db.refresh(user)
    else:
        # Создание нового пользователя
        user = User(
            telegram_id=str(init_data.id),
            first_name=init_data.first_name,
            second_name=init_data.last_name,
            username=init_data.username,
            last_active=datetime.now(),  # Обновляем время последнего действия
            created_at=datetime.now(),  # Добавляет дату создания аккаунта
            is_active=True  # Устанавливаем is_active в True для нового пользователя
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # Переоброзование времени последней активности в строку для передачи через json
    user.last_active = user.last_active.isoformat()
    # Создаем ответ с использованием UserResponse
    user_response = UserResponse.from_orm(user)

    # Обновляем токен и устанавливаем его в куки
    response = JSONResponse(content=user_response.dict())
    response = update_token(response, user.id)
    
    return response
