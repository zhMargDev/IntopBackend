import os, shortuuid
import firebase_conf

from firebase_admin import auth, db, storage
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
from utils.user import get_current_user
from utils.services_categories import get_services_categories
from utils.services import get_payment_method, get_service_by_id, update_service_in_db, delete_service_from_db, delete_picture_from_storage

router = APIRouter()

@router.get("/all", 
             summary="Получение всех сервисов или конкретного сервиса по id",
             description=services_documentation.get_all,
             response_model=List[ServiceSchema])
async def get_services(
        id: Optional[str] = Query(None, description="ID сервиса для фильтрации"),
        service_category_id: Optional[int] = Query(None, description="ID сервиса для фильтрации"),
        min_price: Optional[float] = Query(None, description="Минимальная цена для фильтрации"),
        max_price: Optional[float] = Query(None, description="Максимальная цена для фильтрации"),
        payment_method_id: Optional[int] = Query(None, description="Метод оплаты для фильтрации")
    ):
    # Если указан id, находим и возвращаем услугу по id
    if id is not None:
        ref = db.reference(f'/services/{id}')
        data = ref.get()

        if not data:
            raise HTTPException(status_code=404, detail="Услуга по указанному id не найдена.")

        return [data]

    # Получаем ссылку на узел услуг
    ref = db.reference('/services')
    data = ref.get()

    if not data:
        raise HTTPException(status_code=404, detail="Услуги не найдены.")

    # Преобразуем данные в список
    services = list(data.values())

    # Применяем фильтры
    if service_category_id is not None:
        services = [service for service in services if service.get('service_category_id') == service_category_id]
    if payment_method_id is not None:
        services = [service for service in services if service.get('payment_method_id') == payment_method_id]
    if min_price is not None:
        services = [service for service in services if service.get('price') >= min_price]
    if max_price is not None:
        services = [service for service in services if service.get('price') <= max_price]

    # Добавляем к ответу метод оплаты
    for service in services:
        payment_method = await get_payment_method(service.get('payment_method_id'))
        service['payment_method'] = payment_method['method']

    return services


@router.post('/add',
             summary="Добавление новой услуги.",
             description=services_documentation.add_new_service)
async def add_new_service(
    uid: str = Depends(get_current_user),
    name: str = Form(...),
    lat: float = Form(...),
    lon: float = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    currency: str = Form(...),
    date: int = Form(None),
    email: str = Form(None),
    phone_number: str = Form(None),
    is_store: bool = Form(...),
    picture: UploadFile = File(...),
    service_category_id: int = Form(...),
    payment_method_id: int = Form(None),
):
    # В uid уже указан id и токен пользователя
    
    # Проверка существования категории сервиса
    service_category = await get_services_categories(id=service_category_id)
    if not service_category:
        raise HTTPException(status_code=404, detail="Категория сервиса не найдена")

    # Проверка существования способа оплаты, если указан
    if payment_method_id:
        if not get_payment_method(payment_method_id):
            raise HTTPException(status_code=404, detail="Такой способа оплаты не найдено.")

    # Генерация уникального идентификатора для нового сервиса
    service_id = shortuuid.uuid()

    def check_id_unice(service_id):
        # Проверка существования идентификатора в базе данных
        while db.reference(f'/services/{service_id}').get() is not None:
            return service_id
        else:
            new_service_id = shortuuid.uuid()
            check_id_unice(new_service_id)
        
    service_id = check_id_unice(service_id)

    # Загрузка картинки в Firebase Storage
    bucket = storage.bucket()
    blob = bucket.blob(f'services/{service_id}/{picture.filename}')
    blob.upload_from_file(picture.file, content_type=picture.content_type)

    # Получение публичного URL загруженной картинки
    picture_url = blob.public_url

    # Сохранение информации о новой услуге в базу данных
    service_data = {
        'id': service_id,
        'rating_count': 0,
        'views_count': 0,
        'is_active': False,
        'name': name,
        'lat': lat,
        'lon': lon,
        'description': description,
        'price': price,
        'currency':currency,
        'owner_id': uid,
        'date': date,
        'email': email,
        'phone_number': phone_number,
        'is_store': is_store,
        'picture_url': picture_url,
        'service_category_id': service_category_id,
        'payment_method_id': payment_method_id,
        'created_at': datetime.now().isoformat()
    }

    # Добавляем новую запись в Firebase Realtime Database
    db.reference(f'/services/{service_id}').set(service_data)

    return {"message": "Услуга успешно добавлена", "service": service_data}

@router.put('/update',
            summary="Обновление сервиса.",
            description=services_documentation.update_service)
async def update_service(
    uid: str = Depends(get_current_user),
    service_id: str = Form(...),
    name: Optional[str] = Form(None),
    lat: Optional[float] = Form(None),
    lon: Optional[float] = Form(None),
    description: Optional[str] = Form(None),
    price: Optional[float] = Form(None),
    date: Optional[int] = Form(None),
    picture: Optional[bytes] = File(None),
    phone_number: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
):
    # Получаем сервис по service_id
    service = await get_service_by_id(service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Сервис не найден.")

    # Проверяем, что owner_id сервиса совпадает с uid текущего пользователя
    if service.get('owner_id') != uid:
        raise HTTPException(status_code=403, detail="У вас нет прав для обновления этого сервиса.")

    # Обновляем данные сервиса, которые были переданы в запросе
    updated_data = {}
    if name is not None:
        updated_data['name'] = name
    if lat is not None:
        updated_data['lat'] = lat
    if lon is not None:
        updated_data['lon'] = lon
    if description is not None:
        updated_data['description'] = description
    if price is not None:
        updated_data['price'] = price
    if date is not None:
        updated_data['date'] = date
    if phone_number is not None:
        updated_data['phone_number'] = phone_number
    if email is not None:
        updated_data['email'] = email

    # Если передана картинка, загружаем её в Firebase Storage и обновляем URL картинки
    if picture is not None:
        bucket = storage.bucket()
        blob = bucket.blob(f'services/{service_id}/{shortuuid.uuid()}.jpg')
        blob.upload_from_file(picture, content_type='image/jpeg')
        updated_data['picture_url'] = blob.public_url

    # Обновляем сервис в базе данных
    await update_service_in_db(service_id, updated_data)

    return {"message": "Сервис успешно обновлен", "service": {**service, **updated_data}}


@router.delete('/delete',
               summary="Удаление сервиса.",
               description=services_documentation.delete_service)
async def delete_service(
    request: Request,
    uid: str = Depends(get_current_user)
):
    service_id = request.service_id

    # Получаем сервис по service_id
    service = await get_service_by_id(service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Сервис не найден.")

    # Проверяем, что owner_id сервиса совпадает с uid текущего пользователя
    if service.get('owner_id') != uid:
        raise HTTPException(status_code=403, detail="У вас нет прав для удаления этого сервиса.")

    # Удаляем картинки, связанные с услугой
    picture_url = service.get('picture_url')
    if picture_url:
        await delete_picture_from_storage(service_id, picture_url)

    # Удаляем сервис из базы данных
    await delete_service_from_db(service_id)

    return {"message": "Сервис успешно удален"}

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