import os

from fastapi import APIRouter, Depends, HTTPException, Request, File, UploadFile, Form, Query, Header
from sqlalchemy.orm import Session, joinedload
from starlette.responses import JSONResponse
from datetime import datetime
from typing import List, Optional

from documentation.services import advertisments as advertisments_documentation
from database import get_db
from models.models import Advertisment, User
from schemas.services.advertisments import *
from utils.files import add_domain_to_picture
from utils.token import decode_access_token, update_token

router = APIRouter()

@router.get("/all", 
             summary="Получение всех сервисов или конкретного сервиса по id",
             description=advertisments_documentation.get_all,
             response_model=List[AdvertismentSchema])
async def get_all_advertisments(
        request: Request,
        db: Session = Depends(get_db),
        id: Optional[int] = Query(None, description="ID объявления для фильтрации")
    ):
    # Если указан id, ищем объявление по этому id
    if id is not None:
        advertisment = db.query(Advertisment).filter(Advertisment.id == id).first()
        if not advertisment:
            raise HTTPException(status_code=404, detail="Объявление не найдено")
        
        # Добавляем домен к пути изображения объявления
        if advertisment.picture:
            advertisment.picture = add_domain_to_picture(request, advertisment.picture)
        
        # Добавляем домен к изображению сервиса, если он существует
        if advertisment.service and advertisment.service.picture:
            advertisment.service.picture = add_domain_to_picture(request, advertisment.service.picture)
        
        return [advertisment]
    
    # Если id не указан, возвращаем все объявления
    advertisments = db.query(Advertisment).all()
    
    # Если объявления не найдены, возвращаем 404 ошибку
    if not advertisments:
        raise HTTPException(status_code=404, detail="Объявлений не найдено")
    
    # Добавляем домен к пути изображения для каждого объявления и изображения сервиса
    for advertisment in advertisments:
        # Добавляем домен к изображению объявления
        if advertisment.picture:
            advertisment.picture = add_domain_to_picture(request, advertisment.picture)
        
        # Добавляем домен к изображению сервиса, если он существует
        if advertisment.service and advertisment.service.picture:
            advertisment.service.picture = add_domain_to_picture(request, advertisment.service.picture)
    
    # Возвращаем список объявлений
    return advertisments

@router.post('/add',
             summary="Добавление новой услуги.",
             description=advertisments_documentation.add_new_advertisment)
async def add_new_advertisment(
    user_id: int = Form(...),
    name: str = Form(...),
    location: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    owner_id: int = Form(...),
    timer: int = Form(...),
    picture: bytes = File(...),
    db: Session = Depends(get_db),
    authorization: str = Header(None)
):
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
    
    # Проверка, что owner_id из токена совпадает с owner_id из формы
    if token_user_id != user_id:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    # Проверка что пользовватель существует и активен
    user = db.query(User).filter(User.id == token_user_id).first()

    if not user or not user.is_active:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Путь к папке для сохранения изображений
    upload_dir = "static/advertisements"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    # Генерируем уникальное имя файла
    file_extension = picture.filename.split(".")[-1]
    file_name = f"{name}_{owner_id}.{file_extension}"
    file_path = os.path.join(upload_dir, file_name)

    # Сохраняем файл
    with open(file_path, "wb") as buffer:
        buffer.write(picture.file.read())

    # Создаем новый объект Advertisement
    new_advertisement = Advertisment(
        name=name,
        location=location,
        rating_count=0,
        views_count=0,
        description=description,
        price=price,
        owner_id=owner_id,
        is_active=False,
        timer=timer,
        picture=file_name  # Сохраняем только имя файла без префикса static/
    )

    # Добавляем объект в сессию и сохраняем в базе данных
    db.add(new_advertisement)
    db.commit()
    db.refresh(new_advertisement)

    # Обновляем токен и устанавливаем его в куки
    response = JSONResponse(content={"message": "Объявление успешно создано", "advertisement_id": new_advertisement.id})
    response = update_token(response, token_user_id)
    
    return response