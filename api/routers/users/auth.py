import firebase_admin

from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from firebase_admin import auth, db, credentials, messaging
from firebase_admin.exceptions import FirebaseError

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

class EmailRegistration(BaseModel):
    email: str
    password: str

class PhoneVerification(BaseModel):
    phone_number: str
    code: str

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

        # Возврат сообщения об успешной регистрации
        return {"message": "Пользователь успешно зарегистрирован. Пожалуйста, проверьте вашу почту для подтверждения."}
    except FirebaseError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/register_with_phone",
             summary="Регистрация через email.",
             description=authorization_documentation.register_with_email_description)
async def register_with_phone(data: User):
    try:
        # Создаем учетную запись в Firebase, используя полученный код подтверждения
        credential = auth.PhoneAuthProvider.credential(
            verification_id=data.verification_id,
            verification_code=data.verification_code
        )
        user = await auth.sign_in_with_credential(credential)

        data.created_at = data.created_at.isoformat()
        data.last_active = data.last_active.isoformat()

        user_data_dict = data.dict(exclude={"password", "verification_id", "verification_code"})
        user_data_dict["uid"] = user.uid

        # Сохранение всех данных в Realtime Database
        db.reference("users").child(user.uid).set(user_data_dict)

        return {"message": "Пользователь успешно зарегистрирован через номер телефона."}
    except auth.AuthError as e:
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
