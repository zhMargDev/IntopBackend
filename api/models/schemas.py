from pydantic import BaseModel, EmailStr
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
    email: Optional[EmailStr] = None
    rating: Optional[float] = None
    region_id: Optional[int] = None
    is_verified: Optional[bool] = False

class UserCreate(UserBase):
    # Fields required for creating a new user
    telegram_id: int
    username: str

class UserUpdate(BaseModel):
    telegram_id: Optional[int] = None
    role_id: Optional[int] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    second_name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    avatar: Optional[str] = None
    rating: Optional[float] = None
    region_id: Optional[int] = None

    class Config:
        orm_mode = True

class UserOut(UserBase):
    id: int
    avatar: Optional[str] = None
    last_active: Optional[datetime] = None

    class Config:
        orm_mode = True

class DeleteUserRequest(BaseModel):
    user_id: int
class UserList(BaseModel):
    users: list[UserOut]

class StoreBase(BaseModel):
    name: str
    short_name: str
    llc_name: Optional[str] = None
    address: Optional[str] = None
    region_id: Optional[int] = None
    is_verified: Optional[bool] = False
    category_id: int
    rating: Optional[float] = None  # Оценка магазина

class StoreUpdate(BaseModel):
    name: Optional[str] = None
    short_name: Optional[str] = None
    llc_name: Optional[str] = None
    address: Optional[str] = None
    region_id: Optional[int] = None
    is_verified: Optional[bool] = None
    rating: Optional[float] = None
    category_id: Optional[int] = None

class StoreOut(StoreBase):
    id: int
    owner_id: Optional[int] = None

    class Config:
        orm_mode = True

class StoreList(BaseModel):
    stores: list[StoreOut]