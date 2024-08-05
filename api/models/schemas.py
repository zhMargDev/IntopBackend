from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime

# Pydantic модель для получения данных
class TelegramInitData(BaseModel):
    id: int
    first_name: str
    last_name: str
    username: str

# Схема для ответа по категории
class CategoryOut(BaseModel):
    id: int
    name: str
    subcategories: List['CategoryOut'] = []

    class Config:
        orm_mode = True

class RatingCreate(BaseModel):
    rater_id: int
    rated_id: int
    rating: float = Field(..., gt=0, lt=6)  # Предполагаем, что рейтинг от 1 до 5

class UserGetByFilters(BaseModel):
    id: Optional[int] = None
    telegram_id: Optional[int] = None
    role_id: Optional[int] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    second_name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    region_id: Optional[int] = None
    is_verified: Optional[int] = None