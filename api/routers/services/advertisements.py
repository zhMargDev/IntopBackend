import os

from fastapi import APIRouter, Depends, HTTPException, Request, File, UploadFile, Form, Query, Header
from sqlalchemy.orm import Session, joinedload
from starlette.responses import JSONResponse
from datetime import datetime
from typing import List, Optional

from documentation.services import advertisments as advertisments_documentation
from database import get_db
from models.models import Advertisment, User, BookedService
from schemas.services.advertisments import *
from utils.files import add_domain_to_picture
from utils.token import decode_access_token, update_token

router = APIRouter()

@router.get("/all", 
             summary="Получение всех объявлений или конкретного объявления по id",
             description=advertisments_documentation.get_all,
             response_model=List[AdvertismentSchema])
async def get_advertisments(
        request: Request,
        db: Session = Depends(get_db),
        id: Optional[int] = Query(None, description="ID объявления для фильтрации"),
        service_id: Optional[int] = Query(None, description="ID сервиса для фильтрации"),
        min_price: Optional[float] = Query(None, description="Минимальная цена для фильтрации"),
        max_price: Optional[float] = Query(None, description="Максимальная цена для фильтрации"),
        payment_method: Optional[str] = Query(None, description="Метод оплаты для фильтрации")
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
    
    # Если указаны фильтры, применяем их
    query = db.query(Advertisment)
    
    if service_id is not None:
        query = query.filter(Advertisment.service_id == service_id)
    
    if min_price is not None and max_price is not None:
        if min_price > max_price:
            raise HTTPException(status_code=400, detail="Минимальная цена не может быть больше максимальной цены")
        query = query.filter(Advertisment.price.between(min_price, max_price))
    elif min_price is not None:
        query = query.filter(Advertisment.price >= min_price)
    elif max_price is not None:
        query = query.filter(Advertisment.price <= max_price)
    
    if payment_method is not None:
        query = query.filter(Advertisment.payment_method == payment_method)
    
    advertisments = query.all()
    
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
    lat: float = Form(...),
    lon: float = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    owner_id: int = Form(...),
    date: int = Form(...),
    email: str = Form(None),
    phone_number: str = Form(None),
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
        lat=lat,
        lon=lon,
        rating_count=0,
        views_count=0,
        description=description,
        price=price,
        owner_id=owner_id,
        is_active=False,
        date=date,
        picture=file_name  # Сохраняем только имя файла без префикса static/
    )

    if email is not None:
        new_advertisement.email = email
    if phone_number is not None:
        new_advertisement.phone_number = phone_number

    # Добавляем объект в сессию и сохраняем в базе данных
    db.add(new_advertisement)
    db.commit()
    db.refresh(new_advertisement)

    # Обновляем токен и устанавливаем его в куки
    response = JSONResponse(content={"message": "Объявление успешно создано", "advertisement_id": new_advertisement.id})
    response = update_token(response, token_user_id)
    
    return response

@router.put('/update/{advertisement_id}',
            summary="Обновление объявления.",
            description=advertisments_documentation.update_advertisment)
async def update_advertisment(
    advertisement_id: int,
    user_id: int = Form(...),
    name: str = Form(None),
    lat: float = Form(None),
    lon: float = Form(None),
    description: str = Form(None),
    price: float = Form(None),
    date: int = Form(None),
    picture: bytes = File(None),
    phone_number: str = File(None),
    email: str = File(None),
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

    # Получаем объявление для обновления
    advertisement = db.query(Advertisment).filter(Advertisment.id == advertisement_id).first()

    if not advertisement:
        raise HTTPException(status_code=404, detail="Объявление не найдено")

    # Обновляем поля объявления, если они были переданы
    if name is not None:
        advertisement.name = name
    if lat is not None:
        advertisement.lat = lat
    if lon is not None:
        advertisement.lon = lon
    if description is not None:
        advertisement.description = description
    if price is not None:
        advertisement.price = price
    if date is not None:
        advertisement.date = date
    if phone_number is not None:
        advertisement.phone_number = phone_number
    if email is not None:
        advertisement.email = email

    # Если передано новое изображение, сохраняем его
    if picture is not None:
        upload_dir = "static/advertisements"
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        file_extension = picture.filename.split(".")[-1]
        file_name = f"{name}_{advertisement.owner_id}.{file_extension}"
        file_path = os.path.join(upload_dir, file_name)

        with open(file_path, "wb") as buffer:
            buffer.write(picture.file.read())

        advertisement.picture = file_name

    # Сохраняем изменения в базе данных
    db.commit()
    db.refresh(advertisement)

    # Обновляем токен и устанавливаем его в куки
    response = JSONResponse(content={"message": "Объявление успешно обновлено", "advertisement_id": advertisement.id})
    response = update_token(response, token_user_id)
    
    return response


@router.delete('/delete/{advertisement_id}',
               summary="Удаление объявления.",
               description=advertisments_documentation.delete_advertisment)
async def delete_advertisment(
    advertisement_id: int,
    user_id: int = Form(...),
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

    # Получаем объявление для удаления
    advertisement = db.query(Advertisment).filter(Advertisment.id == advertisement_id).first()

    if not advertisement:
        raise HTTPException(status_code=404, detail="Объявление не найдено")

    # Удаляем изображение, если оно существует
    if advertisement.picture:
        picture_path = os.path.join("static/advertisements", advertisement.picture)
        if os.path.exists(picture_path):
            os.remove(picture_path)

    # Удаляем объявление
    db.delete(advertisement)
    db.commit()

    # Обновляем токен и устанавливаем его в куки
    response = JSONResponse(content={"message": "Объявление успешно удалено", "advertisement_id": advertisement_id})
    response = update_token(response, token_user_id)
    
    return response

@router.post('/book_service',
             summary="Бронирование услуги.",
             description=advertisments_documentation.book_service)
async def book_service(
    booking_data: BookServiceRequest,
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
    
    # Проверка, что user_id из токена совпадает с user_id из запроса
    if token_user_id != booking_data.user_id:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    # Проверка что пользовватель существует и активен
    user = db.query(User).filter(User.id == token_user_id).first()

    if not user or not user.is_active:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Проверка что объявление существует
    advertisement = db.query(Advertisment).filter(Advertisment.id == booking_data.advertisement_id).first()

    if not advertisement:
        raise HTTPException(status_code=404, detail="Объявление не найдено")

    # Создаем новую бронь
    new_booking = BookedService(
        user_id=booking_data.user_id,
        advertisement_id=booking_data.advertisement_id,
        date=booking_data.date,
        time=booking_data.time
    )

    # Добавляем бронь в сессию и сохраняем в базе данных
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)

    # Обновляем токен и устанавливаем его в куки
    response = JSONResponse(content={"message": "Услуга успешно забронирована", "booking_id": new_booking.id})
    response = update_token(response, token_user_id)
    
    return response