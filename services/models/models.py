from sqlalchemy.orm import declarative_base, relationship

# Импорт таблиц из models.tables
from models.tables import (
    services_table
)

# Создание базового класса с использованием декларативной базы
Base = declarative_base()

# Определение класса сервисов
class Services(Base):
    __table__= services_table

    id = services_table.c.id
    title = services_table.c.title
    description = services_table.c.description
    picture = services_table.c.picture