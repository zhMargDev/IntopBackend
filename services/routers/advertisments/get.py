import shutil, os

from fastapi import APIRouter, Depends, HTTPException, Request, File, UploadFile, Form, Query
from sqlalchemy.orm import Session, joinedload
from starlette.responses import JSONResponse
from datetime import datetime
from typing import List, Optional

from documentation import advertisments as advertisments_documentation
from database import get_db
from models.models import Advertisment
from schemas.advertisments import *
from utils.files import add_domain_to_picture

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