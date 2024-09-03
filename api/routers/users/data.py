import shutil, os

from fastapi import APIRouter, Depends, HTTPException, Request, File, UploadFile, Form, Query, Header
from sqlalchemy.orm import Session, joinedload
from starlette.responses import JSONResponse
from datetime import datetime

from database import get_db
from models.models import User
from schemas.user import UserGetByFilters
from utils.token import decode_access_token, update_token
from config import BASE_DIR
from documentation.users import data as user_documentation
from schemas.user import *


router = APIRouter()

@router.get('/my_data', 
             summary="Получени данных пользователя",
             description=user_documentation.get_user_data)
async def get_my_data(db: Session = Depends(get_db), authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=403, detail="Токен доступа отсутствует")

    # Извлечение токена из заголовка Authorization
    token = authorization.split(" ")[1] if len(authorization.split(" ")) > 1 else None

    if not token:
        raise HTTPException(status_code=403, detail="Недействительный токен")

    # Получение user_id из токена
    try:
        payload = decode_access_token(token)
        token_user_id = int(payload['sub'])
    except HTTPException:
        raise HTTPException(status_code=403, detail="Недействительный токен")
    
    user = db.query(User).filter(User.id == token_user_id).first()

    if not user or not user.is_active:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Устанавливаем время последней активности пользователя
    user.last_active = datetime.now()

    db.commit()
    db.refresh(user)

    # Переоброзование времени последней активности и даты создания в строку для передачи через json ! не сохраняем в базе
    user.last_active = user.last_active.isoformat()
    user.created_at = user.created_at.isoformat()

    # Создаем ответ с использованием UserResponse
    user_response = UserResponse.from_orm(user)

    # Обновляем токен и устанавливаем его в куки
    response = JSONResponse(content=user_response.dict())
    response = update_token(response, user.id)
    
    return response

@router.put("/update", 
            summary="Обновление данных пользователя",
            description=user_documentation.update_user)
async def update_user(
        request: Request,
        user_id: int = Form(None),
        first_name: str = Form(None),
        second_name: str = Form(None),
        username: str = Form(None),
        phone_number: str = Form(None),
        email: str = Form(None),
        region_id: int = Form(None),
        avatar: UploadFile = File(None),
        db: Session = Depends(get_db)
    ):
    # Извлечение токена из куки
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=401, detail="Токен доступа отсутствует")

    # Получение user_id из токена
    try:
        payload = decode_access_token(token)
        token_user_id = int(payload['sub'])
    except HTTPException:
        raise HTTPException(status_code=401, detail="Недействительный токен")

    if not user_id or user_id != token_user_id:
        raise HTTPException(status_code=401, detail="Недействительный пользователь")

    # Найти пользователя по user_id
    user = db.query(User).filter(User.id == token_user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Обновление данных пользователя
    if first_name:
        user.first_name = first_name
    if second_name:
        user.second_name = second_name
    if username:
        user.username = username
    if phone_number:
        user.phone_number = phone_number
    if email:
        user.email = email
    if region_id:
        user.region_id = region_id

    # Сохранение аватарки, если она предоставлена
    if avatar:
        # Создание пути для нового аватара
        avatar_filename = f"{token_user_id}{os.path.splitext(avatar.filename)[1]}"  # Сохранение оригинального расширения
        avatar_path = os.path.join(BASE_DIR, 'static', 'users_avatars', avatar_filename)

        # Удаление старого аватара, если он существует
        if user.avatar:
            old_avatar_path = os.path.join(BASE_DIR, 'static', 'users_avatars', os.path.basename(user.avatar.strip('/')))
            if os.path.exists(old_avatar_path):
                os.remove(old_avatar_path)

        # Сохранение нового файла аватара
        with open(avatar_path, 'wb') as out_file:
            shutil.copyfileobj(avatar.file, out_file)

        # Обновляем путь к аватарке в базе данных
        user.avatar = f"/static/users_avatars/{avatar_filename}"

    user.last_active = datetime.now()

    db.commit()
    db.refresh(user)

    # Обновляем токен и устанавливаем его в куки
    response = JSONResponse(content={"message": "Данные пользователя успешно обновлены"})
    response = update_token(response, user.id)

    return response

@router.delete('/deactivate', 
               summary="Деактивация (удаление) аккаунта пользователя",
               description=user_documentation.deactivate_user)
async def deactivate_account(
        request: Request,
        user_id: int = Query(None),
        db: Session = Depends(get_db)
    ):

    # !!!!!!!!!!! Добавить деактивацию всего что связано с пользователем, например его магазин, его товары, товары магазина и тд

    # Извлечение токена из куки
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=401, detail="Токен доступа отсутствует")

    try:
        payload = decode_access_token(token)
        token_user_id = int(payload['sub'])
    except HTTPException:
        raise HTTPException(status_code=401, detail="Недействительный токен")

    # Проверка, если user_id не указан или не совпадает с user_id из токена
    if not user_id or user_id != token_user_id:
        raise HTTPException(status_code=401, detail="Пользователь недействителен")

    # Найти пользователя по user_id
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Деактивировать аккаунт (или удалить его, если требуется)
    # Например, можно установить флаг активности в базе данных
    user.is_active = False
    db.commit()
    db.refresh(user)

    # Удаление токена из куки
    response = JSONResponse(content={"message": "Аккаунт успешно деактивирован"})
    response.set_cookie(key="access_token", value="", expires=0)

    return response

@router.get('/by_filters', 
            summary="Получение пользователей по фильтрам", 
            description=user_documentation.get_users_by_filters)
async def get_users_by_filters(
    filters: UserGetByFilters = Depends(),
    db: Session = Depends(get_db)
):
    # Создаем начальный запрос для получения активных пользователей
    query = db.query(User).filter(User.is_active == True)
    
    # Применяем фильтры, если они указаны
    if filters.id is not None:
        query = query.filter(User.id == filters.id)
    if filters.telegram_id is not None:
        query = query.filter(User.telegram_id == filters.telegram_id)
    if filters.role_id is not None:
        query = query.filter(User.role_id == filters.role_id)
    if filters.username:
        query = query.filter(User.username.ilike(f"%{filters.username}%"))
    if filters.first_name:
        query = query.filter(User.first_name.ilike(f"%{filters.first_name}%"))
    if filters.second_name:
        query = query.filter(User.second_name.ilike(f"%{filters.second_name}%"))
    if filters.phone_number:
        query = query.filter(User.phone_number.ilike(f"%{filters.phone_number}%"))
    if filters.email:
        query = query.filter(User.email.ilike(f"%{filters.email}%"))
    if filters.region_id is not None:
        query = query.filter(User.region_id == filters.region_id)
    if filters.is_verified is not None:
        query = query.filter(User.is_verified == filters.is_verified)

    # Добавляем загрузку связанных данных
    query = query.options(joinedload(User.role), joinedload(User.region), joinedload(User.my_stores))

    # Выполняем запрос и получаем результаты
    users = query.all()

    # Проверяем, есть ли результаты, если нет - возвращаем ошибку 403
    if not users:
        raise HTTPException(status_code=403, detail="Пользователий не найдено")

    return users

