import os, shortuuid
import firebase_conf

from firebase_admin import auth, db, storage
from fastapi import APIRouter, Depends, HTTPException, Request, File, UploadFile, Form, Query, Header
from sqlalchemy.orm import Session, joinedload
from starlette.responses import JSONResponse
from datetime import datetime
from typing import List, Optional

from firebase_conf import firebase
from documentation.services import services as services_documentation
from database import get_db
from models.models import Service, User, BookedService, ServicesCategories, PaymentMethod
from schemas.services.services import *
from utils.files import add_domain_to_picture
from utils.token import decode_access_token, update_token
from utils.user import get_current_user
from utils.services_categories import get_services_categories
from utils.services import get_payment_method, get_service_by_id, update_service_in_db, delete_service_from_db
from utils.main import delete_picture_from_storage

router = APIRouter()

@router.get('/by_filters',
            summary="Получение услуг по фильтрам.",
            description=services_documentation.get_services_by_filters)
async def get_services_by_filters(
    filters: ServicesGetByFilters = Depends()
):
    filters.to_int_fields()
    py_db = firebase.database()
    # Получаем услуги
    services_ref = py_db.child("services").get()
    services = services_ref.val() or {}

    print(type(filters.maxPrice))

    filtered_services = []
    for service_id, service_data in services.items():
        if (
            (filters.category_id is None or service_data["service_category_id"] == filters.category_id) and
            (filters.payment_method_id is None or service_data["payment_method_id"] == filters.payment_method_id) and
            (filters.minPrice is None or service_data["price"] >= filters.minPrice) and
            (filters.maxPrice is None or service_data["price"] <= filters.maxPrice)
        ):
            filtered_services.append(service_data)

    return filtered_services

@router.get("/all", 
             summary="Получение всех сервисов или конкретного сервиса по id",
             description=services_documentation.get_all,
             response_model=List[ServiceSchema])
async def get_services(
        id: Optional[str] = Query(None, description="ID сервиса для фильтрации")):
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

    return services

@router.post('/add',
             summary="Добавление новой услуги.",
             description=services_documentation.add_new_service)
async def add_new_service(
    current_user: dict = Depends(get_current_user),
    uid: str = Form(...),
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
    working_times: list = Form(None)
):
    # Проверка пользователя на авторизованность
    if uid != current_user['uid']:
        raise HTTPException(status_code=401, details="Неиндентифицированный пользователь.")
    
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

    def check_id_unique(service_id):
        # Проверка существования идентификатора в базе данных
        if db.reference(f'/services/{service_id}').get() is not None:
            return check_id_unique(shortuuid.uuid())
        return service_id
        
    service_id = check_id_unique(service_id)

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

    # Если имеются время работы то добавляем их
    if working_times:
        service_data['working_times'] = working_times

    # Добавляем новую запись в Firebase Realtime Database
    db.reference(f'/services/{service_id}').set(service_data)

    return {"message": "Услуга успешно добавлена", "service": service_data}

@router.put('/update',
            summary="Обновление сервиса.",
            description=services_documentation.update_service)
async def update_service(
    current_user: dict = Depends(get_current_user),
    uid: str = Form(...),
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
    working_times: Optional[list] = Form(None)
):
    # Получаем сервис по service_id
    service = await get_service_by_id(service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Сервис не найден.")

    # Проверяем, что owner_id сервиса совпадает с uid текущего пользователя
    if service.get('owner_id') != uid or uid != current_user['uid']:
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
    if working_times is not None:
        updated_data['working_times'] = working_times

    # Если передана картинка, загружаем её в Firebase Storage и обновляем URL картинки
    if picture is not None:
        if updated_data['picture_url']:
            await delete_picture_from_storage(updated_data['picture_url'])

        bucket = storage.bucket()
        blob = bucket.blob(f'services/{service_id}/{picture.filename}')
        blob.upload_from_file(picture, picture.content_type)
        updated_data['picture_url'] = blob.public_url

    # Обновляем сервис в базе данных
    await update_service_in_db(service_id, updated_data)

    return {"message": "Сервис успешно обновлен", "service": {**service, **updated_data}}


@router.delete('/delete',
               summary="Удаление сервиса.",
               description=services_documentation.delete_service)
async def delete_service(
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    
    request_data = await request.json()
    uid = request_data.get('uid')
    service_id = request_data.get('service_id')

    # Получаем сервис по service_id
    service = await get_service_by_id(service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Сервис не найден.")

    # Проверяем, что owner_id сервиса совпадает с uid текущего пользователя
    if service.get('owner_id') != uid or uid != current_user['uid']:
        raise HTTPException(status_code=403, detail="У вас нет прав для удаления этого сервиса.")

    # Удаляем картинки, связанные с услугой
    picture_url = service.get('picture_url')
    if picture_url:
        await delete_picture_from_storage(picture_url)

    # Удаляем сервис из базы данных
    await delete_service_from_db(service_id)

    return {"message": "Сервис успешно удален"}

@router.post('/book_service',
             summary="Бронирование услуги.",
             description=services_documentation.book_service)
async def book_service(
    request: Request,
    current_user: dict = Depends(get_current_user),
):  
    request_data = await request.json()
    uid = request_data.get('uid')
    service_id = request_data.get('service_id')
    date = request_data.get('date')
    time = request_data.get('time')
    
    if current_user['uid'] != uid:
        raise HTTPException(status_code=401, details="Неиндентифицированный пользователь.")

    # Проверяем чтобы пользователь не был владельцем объявления
    if db.reference(f'/services/{service_id}').get()['owner_id'] == uid:
        raise HTTPException(status_code=401, details="Владелец не может забронировать.")

    # Генерация индетфикатора
    booking_id = shortuuid.uuid()

    def check_id_unique(booking_id):
        # Проверка существования идентификатора в базе данных
        if db.reference(f'/booking_services/{booking_id}').get() is not None:
            return check_id_unique(shortuuid.uuid())
        return booking_id
        
    booking_id = check_id_unique(booking_id)

    # Сохранение информации о новой услуге в базу данных
    booking_data = {
        'id': booking_id,
        'user_id': uid,
        'service_id': service_id,
        'date': date,
        'tile': time
    }

    # Добавляем новую запись в Firebase Realtime Database
    db.reference(f'/booking_services/{booking_id}').set(booking_data)

    return {"message": "Услуга успешно забронирована", "booking": booking_data}