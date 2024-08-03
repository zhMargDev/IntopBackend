from pydantic import BaseModel
from typing import List

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