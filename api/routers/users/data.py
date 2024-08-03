import shutil
import os
from fastapi import APIRouter, Depends, HTTPException, Request, File, UploadFile, Form
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from database import get_db
from models.models import User
from utils.token import decode_access_token, update_token
from config import BASE_DIR

router = APIRouter()

@router.put("/update", summary="Обновление данных пользователя")
async def update_user(
        request: Request,
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
        raise HTTPException(status_code=401, detail="Access token is missing")

    # Получение user_id из токена
    try:
        payload = decode_access_token(token)
        user_id = int(payload['sub'])
    except HTTPException:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Найти пользователя по user_id
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

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
        avatar_filename = f"{user_id}{os.path.splitext(avatar.filename)[1]}"  # Сохранение оригинального расширения
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

    db.commit()
    db.refresh(user)

    print(user.email)

    # Обновляем токен и устанавливаем его в куки
    response = JSONResponse(content={"message": "User data updated successfully"})
    response = update_token(response, user.id)

    return response