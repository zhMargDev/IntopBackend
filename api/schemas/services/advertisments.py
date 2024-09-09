from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class ServiceSchema(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    picture: Optional[str] = None

    class Config:
        from_attributes = True

class PaymentMethodSchema(BaseModel):
    id: int
    methods_name: str

    class Config:
        from_attributes = True

class AdvertismentSchema(BaseModel):
    id: int
    name: str
    location: str
    rating_count: Optional[int] = 0
    views_count: Optional[int] = 0
    description: Optional[str] = None
    price: float
    owner_id: int
    is_active: bool
    timer: Optional[int] = None
    picture: Optional[str] = None

    # Вложенные модели
    service: Optional[ServiceSchema] = None
    payment_method: Optional[PaymentMethodSchema] = None

    class Config:
        from_attributes = True

class AdvertisementCreate(BaseModel):
    name: str = Field(..., description="Название объявления")
    location: str = Field(..., description="Местоположение объявления")
    rating_count: int = Field(0, description="Количество оценок")
    views_count: int = Field(0, description="Количество просмотров")
    description: str = Field(..., description="Описание объявления")
    price: float = Field(..., description="Цена")
    owner_id: int = Field(..., description="ID владельца")
    is_active: bool = Field(True, description="Активно ли объявление")
    timer: int = Field(..., description="Таймер")