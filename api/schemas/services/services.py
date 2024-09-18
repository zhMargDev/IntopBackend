from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class ServiceCategorySchema(BaseModel):
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

class ServiceWorkTimesSchema(BaseModel):
    id: int
    service_id: int
    is_morning: bool
    is_day: bool
    is_evening: bool
    time_in_second: int

    class Config:
        from_attributes = True

class ServiceSchema(BaseModel):
    id: str
    name: str
    lat: float
    lon: float
    rating_count: Optional[int] = 0
    views_count: Optional[int] = 0
    description: Optional[str] = None
    price: float
    currency: str
    owner_id: int
    is_active: bool
    date: Optional[int] = None
    picture: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    service_category_id: int
    payment_method_id: int
    is_store: bool
    created_at: str
    payment_method: Optional[str] = None
    working_times: Optional[list] = None

class ServiceCreate(BaseModel):
    name: str = Field(..., description="Название объявления")
    lat: float = Field(..., description="Широта")
    lon: float = Field(..., description="Долгота")
    rating_count: int = Field(0, description="Количество оценок")
    views_count: int = Field(0, description="Количество просмотров")
    description: str = Field(..., description="Описание объявления")
    price: float = Field(..., description="Цена")
    owner_id: int = Field(..., description="ID владельца")
    is_active: bool = Field(True, description="Активно ли объявление")
    date: str = Field(..., description="Дата открытия")
    phone_number: str = Field(..., description="Номер телефона")
    email: str = Field(..., description="Эл почта")
    is_store: bool = Field(..., description="Является ли объявление магазином")
    picture: Optional[str] = Field(None, description="URL изображения")
    service_id: int = Field(..., description="ID категории сервиса")
    payment_method_id: Optional[int] = Field(None, description="ID способа оплаты")

class BookServiceRequest(BaseModel):
    uid: str = Field(..., description="ID пользователя, который бронирует услугу")
    service_id: int = Field(..., description="ID объявления, которое бронируется")
    date: str = Field(..., description="Дата бронирования в формате YYYY-MM-DD")
    time: str = Field(..., description="Время бронирования в формате HH:MM")