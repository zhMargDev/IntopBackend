from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, MetaData, Table
from sqlalchemy.orm import declarative_base, relationship

# Создание экземпляра MetaData
metadata = MetaData()

# Создание базового класса с использованием декларативной базы
Base = declarative_base()

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, MetaData, Table

# Создание экземпляра MetaData
metadata = MetaData()

# Определение таблицы 'roles'
roles_table = Table(
    'roles',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String(255), nullable=False),
    Column('permission', String(255), nullable=False)
)

# Определение таблицы 'users'
users_table = Table(
    'users',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('telegram_id', Integer, unique=True, nullable=True),
    Column('password', String(255), nullable=True),
    Column('role_id', Integer, ForeignKey('roles.id')),
    Column('username', String(255), nullable=True),
    Column('first_name', String(255), nullable=True),
    Column('second_name', String(255), nullable=True),
    Column('phone_number', String(255), nullable=True),
    Column('email', String(255), nullable=True),
    Column('avatar', String(255), nullable=True),
    Column('rating', Float, nullable=True),
    Column('region_id', Integer, ForeignKey('regions.id'), nullable=True),
    Column('is_verified', Boolean, default=False),
    Column('is_active', Boolean, default=True),
    Column('created_at', DateTime, nullable=False),
    Column('last_active', DateTime, nullable=False)
)

# Определение таблицы 'ratings'
ratings_table = Table(
    'ratings',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('rater_id', Integer, nullable=False),
    Column('rated_id', Integer, nullable=False),
    Column('rating', Float, nullable=False)
)

# Определение таблицы 'categories'
categories_table = Table(
    'categories',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String(255), nullable=False),
    Column('parent_id', Integer, ForeignKey('categories.id'), nullable=True)
)

# Определение таблицы 'stores'
stores_table = Table(
    'stores',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String(255), nullable=False),
    Column('short_name', String(100), nullable=False),
    Column('llc_name', String(255), nullable=True),
    Column('store_main_picture', String(255), nullable=True),
    Column('address', String(255), nullable=True),
    Column('region_id', Integer, ForeignKey('regions.id'), nullable=True),
    Column('category_id', Integer, ForeignKey('categories.id'), nullable=False),
    Column('owner_id', Integer, ForeignKey('users.id')),
    Column('rating', Float, nullable=True),
    Column('is_verified', Boolean, default=False),
    Column('created_at', DateTime, nullable=False),
    Column('last_active', DateTime, nullable=False)
)

# Определение таблицы 'store_emails'
store_emails_table = Table(
    'store_emails',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('store_id', Integer, ForeignKey('stores.id')),
    Column('email', String(255), nullable=False),
    Column('email_type', String(50), nullable=False)
)

# Определение таблицы 'store_phone_numbers'
store_phone_numbers_table = Table(
    'store_phone_numbers',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('store_id', Integer, ForeignKey('stores.id')),
    Column('phone_number', String(20), nullable=False),
    Column('phone_type', String(50), nullable=False)
)

# Определение таблицы 'regions'
regions_table = Table(
    'regions',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String(255), nullable=False),
    Column('parent_id', Integer, ForeignKey('regions.id'), nullable=True)
)

# Определение таблицы 'store_managers'
store_managers_table = Table(
    'store_managers',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('store_id', Integer, ForeignKey('stores.id'), nullable=False),
    Column('user_id', Integer, ForeignKey('users.id'), nullable=False),
    Column('privileges_id', Integer, ForeignKey('store_privileges.id'), nullable=False)
)

# Определение таблицы 'store_privileges'
store_privileges_table = Table(
    'store_privileges',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String(255), nullable=False),
    Column('access_level', Integer, nullable=False)
)



# Изменеие таблицы регионов, добавление карты с координатами для отрисовки динамической карты
# Определение таблицы баннеров
# Определение таблицы товаров
# Определение таблицы картинок и видео для товаров
# Определение таблицы избранных товаров пользователя
# Определение таблицы товаров в топе
# Определение таблицы оценок товара с возможностью коментария
# Определение таблицы комментариев товара
# Определение таблицы историй
# Определение табоицы картинок и видео для историй
# Определение таблицы чатов
# Определение таблицы сообщений чатов
# Определение таблицы картинок в чатах
# Определение таблицы языков
# Определение таблицы локализации


"""SERVICES"""

# Таблица сервисов
services_categories_table = Table(
    'services_categories',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('title', String(255)),
    Column('description', String(255)),
    Column('picture', String(255)),
)

# Такблица способов оплаты
payment_methodes_table = Table(
    'payment_methodes',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('method_name', String(255))
)

# Таблица рейтинга объявления
services_ratings_table = Table(
    'services_ratings',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('service_id', Integer, nullable=False),
    Column('rater_id', Integer, nullable=False)
)

# Таблица количество просмотров
services_views_table = Table(
    'services_views',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('service_id', Integer, nullable=False),
    Column('rater_id', Integer, nullable=False)
)

# Таблица объявлений
services_table = Table(
    'services',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String(255), nullable=False),
    Column('lat', Float, nullable=False),
    Column('lon', Float, nullable=False),
    Column('rating_count', Integer,  default=0, nullable=False),
    Column('views_count', Integer, default=0, nullable=False),
    Column('description', String(3000), nullable=True),
    Column('price', Integer, nullable=False),
    Column('owner_id', Integer, nullable=False),
    Column('is_active', Boolean, nullable=False, default=False),
    Column('date', String(255), nullable=True),
    Column('phone_number', String(255), nullable=True),
    Column('email', String(255), nullable=True),
    Column('is_store', Boolean, nullable=True),
    Column('picture', String(255), nullable=True),
    Column('service_id', Integer, ForeignKey('services.id'), nullable=False),
    Column('payment_method_id', Integer,  ForeignKey('payment_methodes.id'), nullable=True)
)

# Таблица часов работы
services_work_times_table = Table(
    'services_work_times',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('service_id', Integer, nullable=False),
    Column('is_morning', Boolean),
    Column('is_day', Boolean),
    Column('is_evening', Boolean),
    Column('time_in_second', Integer, nullable=False)
)

# Таблица забронированных сервисов
booked_services = Table(
    'booked_services_table',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('user_id', Integer, nullable=False),
    Column('service_id', Integer, nullable=False),
    Column('date', String(255), nullable=False),
    Column('time', Integer, nullable=False),
)
# Определение класса Role, связанного с таблицей 'roles'
class Role(Base):
    __table__ = roles_table

    id = roles_table.c.id
    name = roles_table.c.name
    permission = roles_table.c.permission

    # Связь с пользователями
    users = relationship('User', back_populates='role')

# Определение класса Region, связанного с таблицей 'regions'
class Region(Base):
    __table__ = regions_table

    id = regions_table.c.id
    name = regions_table.c.name
    parent_id = regions_table.c.parent_id

    # Связь с дочерними регионами
    parent = relationship('Region', remote_side=[id], backref='children')
    # Связь с пользователями
    users = relationship('User', back_populates='region')

# Определение класса User, связанного с таблицей 'users'
class User(Base):
    __table__ = users_table

    id = users_table.c.id
    telegram_id = users_table.c.telegram_id
    role_id = users_table.c.role_id
    password = users_table.c.password
    username = users_table.c.username
    first_name = users_table.c.first_name
    second_name = users_table.c.second_name
    phone_number = users_table.c.phone_number
    email = users_table.c.email
    avatar = users_table.c.avatar
    rating = users_table.c.rating
    region_id = users_table.c.region_id
    is_verified = users_table.c.is_verified
    is_active = users_table.c.is_active
    last_active = users_table.c.last_active

    # Связь с ролью
    role = relationship('Role', back_populates='users')
    # Связь с регионом
    region = relationship('Region', back_populates='users')
    # Связь с моделю менеджеров
    store_managers = relationship("StoreManager", back_populates="user")
    # Связь с магазином
    my_stores = relationship("Store", back_populates="owner")

# Определение класса Rating, связанного с таблицей 'ratings'
class Rating(Base):
    __table__ = ratings_table

    id = ratings_table.c.id
    rater_id = ratings_table.c.rater_id
    rated_id = ratings_table.c.rated_id
    rating = ratings_table.c.rating

# Определение класса Category, связанного с таблицей 'categories'
class Category(Base):
    __table__ = categories_table

    id = categories_table.c.id
    name = categories_table.c.name
    parent_id = categories_table.c.parent_id

    # Связь с дочерними категориями
    parent = relationship('Category', remote_side=[id], backref='children')

# Определение класса Store, связанного с таблицей 'stores'
class Store(Base):
    __table__ = stores_table

    id = stores_table.c.id
    name = stores_table.c.name
    short_name = stores_table.c.short_name
    llc_name = stores_table.c.llc_name
    store_main_picture = stores_table.c.store_main_picture
    address = stores_table.c.address
    region_id = stores_table.c.region_id
    category_id = stores_table.c.category_id
    owner_id = stores_table.c.owner_id
    rating = stores_table.c.rating
    is_verified = stores_table.c.is_verified
    created_at = stores_table.c.created_at
    last_active = stores_table.c.last_active

    # Связь с эл. почтами
    emails = relationship('StoreEmail', back_populates="store")
    # Связь с номерами телефонов
    phone_numbers = relationship('StorePhoneNumber', back_populates="store")
    #Связь с менеджерами 
    managers = relationship('StoreManager', back_populates="store")
    # Связь с создателем
    owner = relationship('User', back_populates="my_stores")

# Определение класса StoreEmail, связанного с таблицей 'store_emails'
class StoreEmail(Base):
    __table__ = store_emails_table

    id = store_emails_table.c.id
    store_id = store_emails_table.c.store_id
    email = store_emails_table.c.email
    email_type = store_emails_table.c.email_type

    # Связь с магазином
    store = relationship('Store', back_populates="emails")

# Определение класса StorePhoneNumber, связанного с таблицей 'store_phone_numbers'
class StorePhoneNumber(Base):
    __table__ = store_phone_numbers_table

    id = store_phone_numbers_table.c.id
    store_id = store_phone_numbers_table.c.store_id
    phone_number = store_phone_numbers_table.c.phone_number
    phone_type = store_phone_numbers_table.c.phone_type

    # Связь с магазином
    store = relationship('Store', back_populates="phone_numbers")

# Определение класса StorePrivilege, связанного с таблицей 'store_privileges'
class StorePrivilege(Base):
    __table__ = store_privileges_table

    id = store_privileges_table.c.id
    name = store_privileges_table.c.name
    access_level = store_privileges_table.c.access_level

    # Связь с менеджером
    manager = relationship('StoreManager', back_populates="privileges")

# Определение класса StoreManager, связанного с таблицей 'store_managers'
class StoreManager(Base):
    __table__ = store_managers_table

    id = store_managers_table.c.id
    store_id = store_managers_table.c.store_id
    user_id = store_managers_table.c.user_id
    privileges_id = store_managers_table.c.privileges_id

    # Связь с приыилегиями
    privileges = relationship('StorePrivilege', back_populates="manager")
    # Связь с магазином
    store = relationship('Store', back_populates="managers")
    # Связь с пользователем
    user = relationship("User", back_populates="store_managers")


"""SERVICES"""
# Определение класса сервисов
class ServicesCategories(Base):
    __table__= services_categories_table

    id = services_categories_table.c.id
    title = services_categories_table.c.title
    description = services_categories_table.c.description
    picture = services_categories_table.c.picture

    service = relationship('Service', back_populates='service_category')

# Определение таблицы способов оплаты
class PaymentMethod(Base):
    __table__ = payment_methodes_table

    id = payment_methodes_table.c.id
    methods_name = payment_methodes_table.c.method_name

    service = relationship('Service', back_populates='payment_method')

# Определение таблицы рейтинга объявления
class ServiceRating(Base):
    __table__ = services_ratings_table

    id = services_ratings_table.c.id
    service_id = services_ratings_table.c.service_id
    rater_id = services_ratings_table.c.rater_id

# Определение таблицы количество просмотров
class ServiceViews(Base):
    __table__ = services_views_table

    id = services_views_table.c.id
    service_id = services_views_table.c.service_id
    rater_id = services_views_table.c.rater_id

# Определение таблицы объявлений
class Service(Base):
    __table__ = services_table

    id = services_table.c.id
    name = services_table.c.name
    lat = services_table.c.lat
    lon = services_table.c.lon
    rating_count = services_table.c.rating_count
    views_count = services_table.c.views_count
    description = services_table.c.description
    price = services_table.c.price
    owner_id = services_table.c.owner_id
    is_active = services_table.c.is_active
    date = services_table.c.date
    picture = services_table.c.picture
    is_store = services_table.c.is_store
    phone_number = services_table.c.phone_number
    email = services_table.c.email

    # Связь с сервисом
    service_category = relationship('Services', back_populates='service')
    # Связь с способом оплаты
    payment_method = relationship('PaymentMethod', back_populates='service')
    # Связь с временем работы
    work_times = relationship('ServiceWorkTimes', back_populates='service')

# Определение таблицы рабочих часов объявления сервиса
class ServiceWorkTimes(Base):
    __table__ = services_work_times_table

    id = services_work_times_table.c.id
    service_id = services_work_times_table.c.service_id
    is_morning = services_work_times_table.c.is_morning
    is_day = services_work_times_table.c.is_day
    is_evening = services_work_times_table.c.is_evening
    time_in_second = services_work_times_table.c.time_in_second

    # Связь с объявлением сервиса
    service = relationship('Service', back_populates='work_times')

# Определение таблицы забронированных сервисов
class BookedService(Base):
    __table__ = booked_services

    id = booked_services.c.id
    user_id = booked_services.c.user_id
    service_id = booked_services.c.service_id
    date = booked_services.c.date 
    time = booked_services.c.time