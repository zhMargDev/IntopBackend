from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from database import get_db
from models.models import User, Role
from schemas.user import *
from utils.token import decode_access_token, update_token
from schemas.sms import *
from documentation.users import auth as authorization_documentation

router = APIRouter()

# Инициализация CryptContext для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    # Хеширование пароля
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    # Проверка 2х паролей с хешированием
    return pwd_context.verify(plain_password, hashed_password)

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

# Почта отправка смс
@router.post("/email/sms", 
             summary="Отправка кода подтверждения на email.",
             description=authorization_documentation.email_sms)
async def email_sms(request: EmailSMSRequest, db: Session = Depends(get_db)):
    # Проверка валидности электронной почты
    if not request.email:
        raise HTTPException(status_code=401, detail="Электронная почта не действительная")
    # Отправка кода подтверждения на эл. почту
    return send_sms_to_email(request, db)

# Почта регистрация
@router.post("/email/reg", 
             summary="Регистрация через электронную почту.",
             description=authorization_documentation.email_reg)
async def email_registration(request: EmailRegistrationRequest, db: Session = Depends(get_db)):
    # Проверка валидности электронной почты
    if not request.email:
        raise HTTPException(status_code=401, detail="Электронная почта не действительная")
        
    # Проверка валидности пароля
    try:
        EmailRegistrationRequest.validate_password(request.password)
    except ValueError as e:
        raise HTTPException(status_code=402, detail=str(e))

    # Проверка на уникальность email и статус is_active
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        if existing_user.is_active:
            raise HTTPException(status_code=403, detail="Пользователь с такой электронной почтой уже существует.")
        else:
            raise HTTPException(status_code=405, detail="Пользователь с такой электронной почтой заблокирован, вы можете его разблокировать.")
        
    # Получение и проверка кода верификации из редиса и запроса
    verification_code = get_verification_code()

    # Если нету кода верификации в базе или в запросе или же они не совпадают
    if not request.code or not verification_code or verification_code != request.code:
        raise HTTPException(status_code=406, detail="Код верификации не подходит")

    # Хеширование пароля
    hashed_password = get_password_hash(request.password)

    # Создание нового пользователя с установкой None для неотправленных полей
    new_user = User(
        email=request.email,
        password=hashed_password,
        username=request.username,
        first_name=request.first_name,
        second_name=request.second_name,
        is_verified=False,
        is_active=True,
        created_at=datetime.now(),
        last_active=datetime.now()
    )

    # Добавление пользователя в базу данных
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Переоброзование времени последней активности в строку для передачи через json
    new_user.last_active = new_user.last_active.isoformat()
    # Создаем ответ с использованием UserResponse
    user_response = UserResponse.from_orm(new_user)

    # Обновляем токен и устанавливаем его в куки
    response = JSONResponse(content=user_response.dict())
    response = update_token(response, new_user.id)
    
    return response

# Почта вход
@router.post("/email/login", 
             summary="Авторизация через электронную почту.",
             description=authorization_documentation.email_login)
async def email_login(request: EmailLoginRequest, db: Session = Depends(get_db)):
    # Поиск пользователя по электронной почте
    user = db.query(User).filter(User.email == request.email).first()

    # Проверка наличия пользователя
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь с такой электронной почтой не найден.")

    # Проверка правильности пароля
    if not verify_password(request.password, user.password):
        raise HTTPException(status_code=403, detail="Неверный пароль.")
    
    # Получение и проверка кода верификации из редиса и запроса
    verification_code = get_verification_code()

    # Если нету кода верификации в базе или в запросе или же они не совпадают
    if not request.code or not verification_code or verification_code != request.code:
        raise HTTPException(status_code=406, detail="Код верификации не подходит")

    # Обновление времени последней активности
    user.last_active = datetime.now()
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