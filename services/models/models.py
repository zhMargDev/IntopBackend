from sqlalchemy.orm import declarative_base, relationship

# Импорт таблиц из models.tables
from models.tables import *

# Создание базового класса с использованием декларативной базы
Base = declarative_base()

# Определение класса сервисов
class Services(Base):
    __table__= services_table

    id = services_table.c.id
    title = services_table.c.title
    description = services_table.c.description
    picture = services_table.c.picture

    advertisments = relationship('Advertisment', back_populates='service')

# Определение таблицы способов оплаты
class PaymentMethod(Base):
    __table__ = payment_methodes_table

    id = payment_methodes_table.c.id
    methods_name = payment_methodes_table.c.method_name

    advertisments = relationship('Advertisment', back_populates='payment_method')

# Определение таблицы рейтинга объявления
class Rating(Base):
    __table__ = ratings_table

    id = ratings_table.c.id
    advertisement_id = ratings_table.c.advertisement_id
    rater_id = ratings_table.c.rater_id

# Определение таблицы количество просмотров
class Views(Base):
    __table__ = views_table

    id = views_table.c.id
    advertisement_id = views_table.c.advertisement_id
    rater_id = views_table.c.rater_id

# Определение таблицы объявлений
class Advertisment(Base):
    __table__ = advertisements_table

    id = advertisements_table.c.id
    name = advertisements_table.c.name
    location = advertisements_table.c.location
    rating_count = advertisements_table.c.rating_count
    views_count = advertisements_table.c.views_count
    description = advertisements_table.c.description
    price = advertisements_table.c.price
    owner_id = advertisements_table.c.owner_id
    is_active = advertisements_table.c.is_active
    timer = advertisements_table.c.timer
    picture = advertisements_table.c.picture

    # Связь с сервисом
    service = relationship('Services', back_populates='advertisments')
    # Связь с способом оплаты
    payment_method = relationship('PaymentMethod', back_populates='advertisments')
