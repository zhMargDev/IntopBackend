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

class AdvertisementsWorkTimes(BaseModel):
    id: int
    advertisement_id: int
    is_morning: bool
    is_day: bool
    is_evening: bool
    time_in_second: int

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
    date: Optional[str] = None
    picture: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None

    # Вложенные модели
    service: Optional[ServiceSchema] = None
    payment_method: Optional[PaymentMethodSchema] = None
    work_times: Optional[AdvertisementsWorkTimes] = None

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
    date: str = Field(..., description="Дата открытия")
    phone_number: str = Field(..., description="Номер телефона")
    email: str = Field(..., description="Эл почта")

class BookServiceRequest(BaseModel):
    user_id: int = Field(..., description="ID пользователя, который бронирует услугу")
    advertisement_id: int = Field(..., description="ID объявления, которое бронируется")
    date: str = Field(..., description="Дата бронирования в формате YYYY-MM-DD")
    time: str = Field(..., description="Время бронирования в формате HH:MM")