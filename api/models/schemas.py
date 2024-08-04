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
