from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import Base

# Создание подключения к базе данных
engine = create_engine("postgresql://intop:ai5JeI9ahng1ohV1@localhost:5432/intop_db")

# Создание фабрики сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создание всех таблиц в базе данных
# Base.metadata.create_all(engine)

# Функция для получения сессии базы данных
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()