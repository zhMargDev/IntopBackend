from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, MetaData, Table

# Создание экземпляра MetaData
metadata = MetaData()

# Таблица сервисов
services_table = Table(
    'services',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('title', String(255)),
    Column('description', String(255)),
    Column('picture', String(255)),
)