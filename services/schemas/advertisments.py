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