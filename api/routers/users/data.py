import shutil, os, shortuuid
import firebase_conf

from firebase_admin import auth, db, storage
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
from utils.user import get_current_user
from utils.main import delete_picture_from_storage


router = APIRouter()

async def update_last_active(db: db.Reference, uid: str):
    """
    Обновляет поле last_active для пользователя по UID.

    Args:
        db: Ссылка на корневой узел базы данных Firebase.
        uid: UID пользователя.
    """

    # Получение ссылки на узел пользователя по UID
    user_ref = db.child(f"users/{uid}")

    # Словарь с новыми данными
    new_data = {"last_active": datetime.now().isoformat()}

    # Обновление данных пользователя
    user_ref.update(new_data)




@router.get('/my_data/{uid}', 
             summary="Получение данных пользователя по UID",
             description=user_documentation.get_user_data)
async def get_my_data(
        uid: str,
        current_user: dict = Depends(get_current_user),
    ):
    """
    Получает данные пользователя и обновляет время последней активности.

    Args:
        uid: UID пользователя.

    Returns:
        dict: Словарь с данными пользователя.
    """
    if current_user['uid'] != uid:
        raise HTTPException(status_code=401, details="Неидентифицированный пользователь.")

    try:
        # Получаем данные пользователя из Realtime Database
        user_ref = db.reference(f"users/{uid}")
        user_data = user_ref.get()

        # Обновляем время последней активности
        user_data["last_active"] = datetime.now().isoformat()

        # Записываем обновленные данные в базу
        user_ref.set(user_data)

        return user_data
    except auth.AuthError as e:
        raise HTTPException(status_code=401, detail="Недействительный UID")


@router.put("/update", 
            summary="Обновление данных пользователя",
            description=user_documentation.update_user)
async def update_user(
        current_user: dict = Depends(get_current_user),
        uid: str = Form(...),
        first_name: str = Form(None),
        last_name: str = Form(None),
        username: str = Form(None),
        phone_number: str = Form(None),
        email: str = Form(None),
        region_id: int = Form(None),
        avatar: UploadFile = File(None),
    ):
    """
    Получает новые данные пользователя и обновляет время последней активности.

    Args:
        uid: UID пользователя.
        - отсальные данные
    Returns:
        dict: Словарь с данными пользователя.
    """

    try:
        if current_user['uid'] != uid:
            raise HTTPException(status_code=401, details="Неидентифицированный пользователь.")
        # Получаем данные пользователя из Realtime Database
        user_ref = db.reference(f"users/{uid}")
        user_data = user_ref.get()

        # Проверяем отправлен ли параметр и изменяем его
        if first_name:
            user_data['first_name'] = first_name
        if last_name:
            user_data['last_name'] = last_name
        if username:
            user_data['username'] = username
        if phone_number:
            user_data['phone_number'] = phone_number
        if email:
            user_data['email'] = email
        if region_id:
            user_data['region_id'] = region_id

        if avatar:
            # Если у пользователя была картинка удаляем его
            if user_data['avatar']:
               await delete_picture_from_storage(user_data['avatar'])
            
            # Сохраняем новую картинку
            bucket = storage.bucket()
            # Используем исходное имя файла
            file_name = avatar.filename
            blob = bucket.blob(f'users/{uid}/{file_name}')
            blob.upload_from_file(avatar.file, avatar.content_type)
            user_data['avatar'] = blob.public_url

        # Обновляем время последней активности
        user_data["last_active"] = datetime.now().isoformat()

        # Записываем обновленные данные в базу
        user_ref.set(user_data)

        return user_data
    except auth.AuthError as e:
        raise HTTPException(status_code=401, detail="Недействительный UID")

@router.delete('/deactivate',
               summary="Деактивация (удаление) аккаунта пользователя",
               description=user_documentation.deactivate_user)
async def deactivate_account(
        request: Request,
        current_user: dict = Depends(get_current_user),
    ):
    try:
        if current_user['uid'] != request.uid:
            raise HTTPException(status_code=401, details="Неидентифицированный пользователь.")
        # Получить пользователя по UID
        user = auth.get_user(request.uid)

        # Деактивировать пользователя
        user.disabled = True
        user.update()

        return {"message": "Аккаунт успешно удалён."}

    except auth.AuthError:
        raise HTTPException(status_code=401, detail="Недействительный UID")

@router.get('/by_filters', 
            summary="Получение пользователей по фильтрам", 
            description=user_documentation.get_users_by_filters)
async def get_users_by_filters(
    filters: UserGetByFilters = Depends(),
):
    """Получает пользователей из Firebase Realtime Database по заданным фильтрам.

    Аргументы:
        filters: Объект с фильтрами для поиска пользователей.

    Возвращает:
        Список объектов User, соответствующих фильтрам.
        Если пользователей не найдено, выбрасывается исключение HTTPException с кодом 404.
    """

    # Получаем ссылку на узел пользователей
    ref = db.reference('/users')

    query = ref

    # Применяем фильтры
    if filters.uid is not None:
        query = query.order_by_child('uid').equal_to(filters.uid)
    if filters.role is not None:
        query = query.order_by_child('role').equal_to(filters.role)
    if filters.username:
        query = query.order_by_child('username').start_at(filters.username).end_at(filters.username + '\uf8ff')
    if filters.first_name:
        query = query.order_by_child('first_name').start_at(filters.first_name).end_at(filters.first_name + '\uf8ff')
    if filters.last_name:
        query = query.order_by_child('last_name').start_at(filters.last_name).end_at(filters.last_name + '\uf8ff')
    if filters.phone_number:
        query = query.order_by_child('phone_number').start_at(filters.phone_number).end_at(filters.phone_number + '\uf8ff')
    if filters.email:
        query = query.order_by_child('email').start_at(filters.email).end_at(filters.email + '\uf8ff')
    if filters.region_id is not None:
        query = query.order_by_child('region_id').equal_to(filters.region_id)

    # Получаем результаты
    snapshot = await query.get()

    # Преобразуем результаты в объекты User, исключая пароль
    users = []
    async for user_data in snapshot.each():
        user_data = user_data.val()
        user_data.pop('password', None)  # Удаляем поле password, если оно существует
        user = User(**user_data)
        users.append(user)

    if not users:
        raise HTTPException(status_code=404, detail="Пользователи не найдены")

    return users

