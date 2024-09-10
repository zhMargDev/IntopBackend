from fastapi import APIRouter, HTTPException, Depends, Request, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from models.models import ServicesCategories
from utils.token import decode_access_token, update_token
from documentation.services import services_categories as services_categories_documentation
from schemas.services.services_categories import *
from utils.files import add_domain_to_picture

router = APIRouter()


@router.get("/all", 
             summary="Получение всех сервисов или конкретного сервиса по id",
             description=services_categories_documentation.get_all_services_categories,
             response_model=List[ServiceCategoryResponse])
async def get_all_services_categories(
        request: Request,
        db: Session = Depends(get_db),
        id: Optional[int] = Query(None, description="ID сервиса для фильтрации")
    ):
    # Если указан id, ищем сервис по этому id
    if id is not None:
        service_category = db.query(ServicesCategories).filter(ServicesCategories.id == id).first()
        if not service_category:
            raise HTTPException(status_code=404, detail="Сервис не найден")
        # Добавляем домен к пути изображения
        service_category.picture = add_domain_to_picture(request, service_category.picture)
        return [service_category]
    
    # Если id не указан, возвращаем все сервисы
    services_categories = db.query(ServicesCategories).all()
    
    # Если сервисы не найдены, возвращаем 404 ошибку
    if not services_categories:
        raise HTTPException(status_code=404, detail="Сервисов не найдено")
    
    # Добавляем домен к пути изображения для каждого сервиса
    for service_category in services_categories:
        service_category.picture = add_domain_to_picture(request, service_category.picture)
    
    # Возвращаем список сервисов
    return services_categories