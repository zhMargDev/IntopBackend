from fastapi import APIRouter, HTTPException, Depends, Request, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from models.models import Services
from utils.token import decode_access_token, update_token
from documentation import services as services_documentation
from schemas.services import *
from utils.files import add_domain_to_picture

router = APIRouter()


@router.get("/all", 
             summary="Получение всех сервисов или конкретного сервиса по id",
             description=services_documentation.get_all_services,
             response_model=List[ServiceResponse])
async def get_all_services(
        request: Request,
        db: Session = Depends(get_db),
        id: Optional[int] = Query(None, description="ID сервиса для фильтрации")
    ):
    # Если указан id, ищем сервис по этому id
    if id is not None:
        service = db.query(Services).filter(Services.id == id).first()
        if not service:
            raise HTTPException(status_code=404, detail="Сервис не найден")
        # Добавляем домен к пути изображения
        service.picture = add_domain_to_picture(request, service.picture)
        return [service]
    
    # Если id не указан, возвращаем все сервисы
    services = db.query(Services).all()
    
    # Если сервисы не найдены, возвращаем 404 ошибку
    if not services:
        raise HTTPException(status_code=404, detail="Сервисов не найдено")
    
    # Добавляем домен к пути изображения для каждого сервиса
    for service in services:
        service.picture = add_domain_to_picture(request, service.picture)
    
    # Возвращаем список сервисов
    return services