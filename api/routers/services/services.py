import os

from fastapi import APIRouter, Depends, HTTPException, Request, File, UploadFile, Form, Query, Header
from sqlalchemy.orm import Session, joinedload
from starlette.responses import JSONResponse
from datetime import datetime
from typing import List, Optional

from documentation.services import services as services_documentation
from database import get_db
from models.models import Service, User, BookedService, ServicesCategories, PaymentMethod
from schemas.services.services import *
from utils.files import add_domain_to_picture
from utils.token import decode_access_token, update_token

router = APIRouter()

@router.get("/all", 
             summary="Получение всех сервисов или конкретного сервиса по id",
             description=services_documentation.get_all,
             response_model=List[ServiceSchema])
async def get_services(
        request: Request,
        db: Session = Depends(get_db),
        id: Optional[int] = Query(None, description="ID сервиса для фильтрации"),
        service_id: Optional[int] = Query(None, description="ID сервиса для фильтрации"),
        min_price: Optional[float] = Query(None, description="Минимальная цена для фильтрации"),
        max_price: Optional[float] = Query(None, description="Максимальная цена для фильтрации"),
        payment_method: Optional[str] = Query(None, description="Метод оплаты для фильтрации")
    ):
    # Если указан id, ищем Сервис по этому id
    if id is not None:
        service = db.query(Service).filter(Service.id == id).first()
        if not service:
            raise HTTPException(status_code=404, detail="Сервис не найдено")
        
        # Добавляем домен к пути изображения сервиса
        if service.picture:
            service.picture = add_domain_to_picture(request, service.picture)
        
        # Добавляем домен к изображению сервиса, если он существует
        if service.service and service.service.picture:
            service.service.picture = add_domain_to_picture(request, service.service.picture)
        
        return [service]
    
    # Если указаны фильтры, применяем их
    query = db.query(Service)
    
    if service_id is not None:
        query = query.filter(Service.service_id == service_id)
    
    if min_price is not None and max_price is not None:
        if min_price > max_price:
            raise HTTPException(status_code=400, detail="Минимальная цена не может быть больше максимальной цены")
        query = query.filter(Service.price.between(min_price, max_price))
    elif min_price is not None:
        query = query.filter(Service.price >= min_price)
    elif max_price is not None:
        query = query.filter(Service.price <= max_price)
    
    if payment_method is not None:
        query = query.filter(Service.payment_method == payment_method)
    services = query.all()
    
    # Если сервиса не найдены, возвращаем 404 ошибку
    if not services:
        raise HTTPException(status_code=404, detail="сервисов не найдено")
    
    # Добавляем домен к пути изображения для каждого сервиса и изображения сервиса
    for service in services:
        # Добавляем домен к изображению сервиса
        if service.picture:
            service.picture = add_domain_to_picture(request, service.picture)
        
        # Добавляем домен к изображению сервиса, если он существует
        if service.service and service.service.picture:
            service.service.picture = add_domain_to_picture(request, service.service.picture)
    
    # Возвращаем список сервисов
    return services

@router.post('/add',
             summary="Добавление новой услуги.",
             description=services_documentation.add_new_service)
async def add_new_service(
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
    is_store: bool = Form(...),
    picture: UploadFile = File(...),
    service_category_id: int = Form(...),
    payment_method_id: int = Form(None),
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
    
    # Проверка что пользователь существует и активен
    user = db.query(User).filter(User.id == token_user_id).first()

    if not user or not user.is_active:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Проверка существования категории сервиса
    service_category = db.query(ServicesCategories).filter(ServicesCategories.id == service_category_id).first()
    if not service_category:
        raise HTTPException(status_code=404, detail="Категория сервиса не найдена")

    # Проверка существования способа оплаты, если указан
    if payment_method_id:
        payment_method = db.query(PaymentMethod).filter(PaymentMethod.id == payment_method_id).first()
        if not payment_method:
            raise HTTPException(status_code=404, detail="Способ оплаты не найден")

    # Путь к папке для сохранения изображений
    upload_dir = "static/services"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    # Генерируем уникальное имя файла
    file_extension = picture.filename.split(".")[-1]
    file_name = f"{name}_{owner_id}.{file_extension}"
    file_path = os.path.join(upload_dir, file_name)

    # Сохраняем файл
    with open(file_path, "wb") as buffer:
        buffer.write(await picture.read())

    # Создаем новый объект service
    new_service = Service(
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
        is_store=is_store,
        picture=file_name,  # Сохраняем только имя файла без префикса static/
        service_category_id=service_category_id,
        payment_method_id=payment_method_id
    )

    if email is not None:
        new_service.email = email
    if phone_number is not None:
        new_service.phone_number = phone_number

    # Добавляем объект в сессию и сохраняем в базе данных
    db.add(new_service)
    db.commit()
    db.refresh(new_service)

    # Обновляем токен и устанавливаем его в куки
    response = JSONResponse(content={"message": "Сервис успешно создан", "service_id": new_service.id})
    response = update_token(response, token_user_id)
    
    return response

@router.put('/update/{service_id}',
            summary="Обновление сервиса.",
            description=services_documentation.update_service)
async def update_service(
    service_id: int,
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

    # Получаем Сервис для обновления
    service = db.query(Service).filter(Service.id == service_id).first()

    if not service:
        raise HTTPException(status_code=404, detail="Сервис не найдено")

    # Обновляем поля сервиса, если они были переданы
    if name is not None:
        service.name = name
    if lat is not None:
        service.lat = lat
    if lon is not None:
        service.lon = lon
    if description is not None:
        service.description = description
    if price is not None:
        service.price = price
    if date is not None:
        service.date = date
    if phone_number is not None:
        service.phone_number = phone_number
    if email is not None:
        service.email = email

    # Если передано новое изображение, сохраняем его
    if picture is not None:
        upload_dir = "static/services"
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        file_extension = picture.filename.split(".")[-1]
        file_name = f"{name}_{service.owner_id}.{file_extension}"
        file_path = os.path.join(upload_dir, file_name)

        with open(file_path, "wb") as buffer:
            buffer.write(picture.file.read())

        service.picture = file_name

    # Сохраняем изменения в базе данных
    db.commit()
    db.refresh(service)

    # Обновляем токен и устанавливаем его в куки
    response = JSONResponse(content={"message": "Сервис успешно обновлено", "service_id": service.id})
    response = update_token(response, token_user_id)
    
    return response


@router.delete('/delete/{service_id}',
               summary="Удаление сервиса.",
               description=services_documentation.delete_service)
async def delete_service(
    service_id: int,
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

    # Получаем Сервис для удаления
    service = db.query(Service).filter(Service.id == service_id).first()

    if not service:
        raise HTTPException(status_code=404, detail="Сервис не найдено")

    # Удаляем изображение, если оно существует
    if service.picture:
        picture_path = os.path.join("static/services", service.picture)
        if os.path.exists(picture_path):
            os.remove(picture_path)

    # Удаляем Сервис
    db.delete(service)
    db.commit()

    # Обновляем токен и устанавливаем его в куки
    response = JSONResponse(content={"message": "Сервис успешно удалено", "service_id": service_id})
    response = update_token(response, token_user_id)
    
    return response

@router.post('/book_service',
             summary="Бронирование услуги.",
             description=services_documentation.book_service)
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

    # Проверка что Сервис существует
    service = db.query(Service).filter(Service.id == booking_data.service_id).first()

    if not service:
        raise HTTPException(status_code=404, detail="Сервис не найдено")

    # Создаем новую бронь
    new_booking = BookedService(
        user_id=booking_data.user_id,
        service_id=booking_data.service_id,
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