from starlette.responses import JSONResponse
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from typing import  List, Optional
from models.models import Store, User
from models.schemas import StoreOut
from database import get_db
from utils.token import decode_access_token, update_token

router = APIRouter()

def check_required_params(name: Optional[str], short_name: Optional[str], category_id: Optional[int]) -> List[str]:
    missing_params = []
    
    if not name:
        missing_params.append("name")
    if not short_name:
        missing_params.append("short_name")
    if category_id is None:
        missing_params.append("category_id")
    
    return missing_params

@router.post("/create_store", response_model=int, summary="Создание нового магазина",
        description="""
        Создает новый магазин с указанными параметрами. 
        
        **Обязательные параметры:**
        - `name`: Название магазина.
        - `short_name`: Краткое название магазина.
        - `category_id`: Идентификатор категории магазина.
        
        **Необязательные параметры:**
        - `region_id`: Идентификатор региона магазина. Если не указан, используется регион пользователя.
        
        **Проверка:**
        - Проверяется наличие JWT токена в куки.
        - Проверяется роль пользователя. Пользователь должен иметь разрешение 'seller' и быть подтвержденным.
        - Если отсутствуют обязательные параметры, возвращается ошибка с деталями недостающих параметров.
        - Если не указан `region_id`, используется регион из данных пользователя. Если регион отсутствует, возвращается ошибка.
        - Если все проверки пройдены, создается новый магазин и возвращается его идентификатор.
        
        **Ошибки:**
        - `400 Bad Request`: Отсутствуют обязательные параметры или `region_id` не указан.
        - `401 Unauthorized`: JWT токен отсутствует или недействителен, пользователь не найден.
        - `403 Forbidden`: Пользователь не имеет необходимых прав или не подтвержден.
        """)
async def create_store(
        request: Request,
        name: Optional[str] = None,
        short_name: Optional[str] = None,
        category_id: Optional[int] = None,
        region_id: Optional[int] = None,
        db: Session = Depends(get_db)
    ):
        # Получение JWT токена из куки
        jwt_token = request.cookies.get("access_token")
        if jwt_token is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="JWT токен отсутствует в куки")
    
        # Декодирование токена и получение user_id
        user_id = decode_access_token(jwt_token)
        
        # Получение пользователя из базы данных
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Пользователь не найден")
        
        # Проверка разрешений пользователя
        if user.role.permission != "seller":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав")
    
        if not user.is_verified:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Пользователь не подтвержден")
    
        # Проверка обязательных параметров
        missing_params = check_required_params(name, short_name, category_id)
        if missing_params:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"missing_params": missing_params}
            )
    
        # Установка region_id
        if region_id is None:
            region_id = user.region_id
    
        if region_id is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"missing_params": ["region_id"]})
    
        # Создание нового магазина
        new_store = Store(
            name=name,
            short_name=short_name,
            category_id=category_id,
            region_id=region_id,
            owner_id=user_id,
            rating=None,  # По умолчанию рейтинг неизвестен
            is_verified=False  # По умолчанию новый магазин не подтвержден
        )
    
        try:
            db.add(new_store)
            db.commit()
            db.refresh(new_store)
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ошибка создания магазина")
    
        # Обновление last_active и токена
        user.last_active = datetime.utcnow()
        db.add(user)
        db.commit()
        response = JSONResponse(content={"store_id": new_store.id})
        update_token(response, user_id)
    
        return response