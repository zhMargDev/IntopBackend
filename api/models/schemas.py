from pydantic import BaseModel
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

class UserBase(BaseModel):
    telegram_id: Optional[int] = None
    role_id: Optional[int] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    second_name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    rating: Optional[float] = None

class UserOut(UserBase):
    user_id: int
    avatar: Optional[str] = None
    last_active: datetime

class UserList(BaseModel):
    users: list[UserOut]