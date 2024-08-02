from fastapi import FastAPI
from fastapi_admin.factory import Admin
from fastapi_admin.models import AbstractAdmin
from fastapi_admin.resources import ModelResource
from fastapi_admin.auth import AuthBackend
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy import create_engine

from api.models.models import User  # Импортируйте ваши модели из папки api

app = FastAPI()

# Настройка SQLAlchemy
DATABASE_URL = "postgresql://intop:ai5JeI9ahng1ohV1@postgres:5432/intop_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base: DeclarativeMeta = Base  # Это ваш Base из моделей

# Настройка административного интерфейса
auth_backend = AuthBackend()
admin = Admin(app, engine, auth_backend)

# Ресурсы для административного интерфейса
class UserResource(ModelResource):
    class Meta:
        model = User

# Регистрация ресурсов
admin.add_resource(UserResource)

@app.on_event("startup")
async def on_startup():
    # Инициализация административного интерфейса
    await admin.create_all()

@app.on_event("shutdown")
async def on_shutdown():
    # Завершение работы административного интерфейса
    await admin.close()

# Определение маршрутов
app.include_router(admin.router, prefix="/admin")