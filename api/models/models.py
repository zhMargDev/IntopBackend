from sqlalchemy.orm import declarative_base, relationship

# Импорт таблиц из models.tables
from models.tables import (
    roles_table, users_table, ratings_table, categories_table,
    stores_table, store_emails_table, store_phone_numbers_table, regions_table,
    store_privileges_table, store_managers_table
)

# Создание базового класса с использованием декларативной базы
Base = declarative_base()

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
    address = stores_table.c.address
    region_id = stores_table.c.region_id
    category_id = stores_table.c.category_id
    owner_id = stores_table.c.owner_id
    rating = stores_table.c.rating
    is_verified = stores_table.c.is_verified

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