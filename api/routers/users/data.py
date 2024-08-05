import shutil
import os

from fastapi import APIRouter, Depends, HTTPException, Request, File, UploadFile, Form, Query
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse
from datetime import datetime

from database import get_db
from models.models import User
from models.schemas import UserGetByFilters
from utils.token import decode_access_token, update_token
from config import BASE_DIR

router = APIRouter()

@router.put("/update", summary="Обновление данных пользователя",
            description="""
            Обновляет информацию о пользователе. Необходимо отправить форму с данными, которые требуется обновить.
            При успешном обновлении возвращается сообщение об успешном обновлении.

            **Параметры формы:**
            - `user_id`: Id пользователя для проверки совместимости с токеном, если не отправить то вернёться ошибка
            - `first_name`: Имя пользователя (опционально)
            - `second_name`: Фамилия пользователя (опционально)
            - `username`: Имя пользователя (опционально)
            - `phone_number`: Номер телефона (опционально)
            - `email`: Адрес электронной почты (опционально)
            - `region_id`: Идентификатор региона (опционально)
            - `avatar`: Новый аватар пользователя (опционально)

            ```
            Пример Curl
            curl -v -X PUT "http://localhost:8000/users/update" \
              -H "Content-Type: multipart/form-data" \
              -b "access_token=your_access_token" \
              -F "user_id"=1 \
              -F "first_name=John" \
              -F "second_name=Doe" \
              -F "username=johndoe" \
              -F "phone_number=1234567890" \
              -F "email=john.doe@example.com"
            ```

            **Ответ:**
            - Если обновление прошло успешно, возвращается сообщение о успешном обновлении данных.

            **Ошибки:**
            - `401 Unauthorized`: Токен доступа отсутствует или недействителен.
            - `401 Unauthorized`: Недействительный пользователь. Отправленный id и id из токена не совпали или id не был отправлен.
            - `404 Not Found`: Пользователь не найден.
            """)
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

@router.delete('/deactivate', summary="Деактивация (удаление) аккаунта пользователя",
               description="""
               Этот эндпоинт деактивирует аккаунт пользователя.

               **Параметры запроса:**
               - `user_id`: Идентификатор пользователя (необязательный параметр). Если не указан, то пользователь поддельный.

               **Пример запроса**
               curl -v -X DELETE "http://localhost:8000/users/deactivate" \
                  -H "Content-Type: application/json" \
                  -b "access_token=your_access_token" \
                  -G \
                  -d "user_id=1"

               **Ответ:**
               - Если деактивация успешна, возвращается сообщение о том, что аккаунт успешно деактивирован и токен доступа удаляется из куки.
               - В случае отсутствия токена, его недействительности или несоответствия `user_id` возвращается ошибка.

               **Ошибки:**
               - `401 Unauthorized`: Токен доступа отсутствует, недействителен или `user_id` не совпадает.
               - `404 Not Found`: Пользователь не найден.
               """)
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

@router.get('/by_filters', summary="Получение пользователей по фильтрам", 
    description="""
        Этот эндпоинт возвращает пользователей по указанным фильтрам.
        Если фильтры не указаны, то вернутся все активные пользователи.

        **Пример запроса**

        ```
        curl -X GET "http://localhost:8000/users/by_filters?id=1&username=johndoe"
        ```

        **Ответ:**
        Если не было ошибки вернётся массив со всеми пользователями, соответствующими фильтрам, которые не удалили (деактивировали) свой аккаунт.
        
        **Ошибки:**
        - `200`: Всё прошло успешно, данные получены.
        - `403`: Пользователей не найдено
        - `500`: Произошла ошибка на сервере.
    """)
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

    # Выполняем запрос и получаем результаты
    users = query.all()

    # Проверяем, есть ли результаты, если нет - возвращаем ошибку 403
    if not users:
        raise HTTPException(status_code=403, detail="Пользователий не найдено")

    return users

