from sqlalchemy import Column, Integer, String, Boolean, MetaData, ForeignKey, Table, DateTime
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

# Создание экземпляра MetaData
metadata = MetaData()

# Создание базового класса с использованием декларативной базы
Base = declarative_base()

# Определение таблицы 'roles'
roles_table = Table(
    'roles',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),  # Первичный ключ, автоинкремент
    Column('name', String(255), nullable=False),  # Имя роли, не может быть пустым
    Column('permission', String(255), nullable=False)  # Разрешение, не может быть пустым
)

# Определение таблицы 'users'
users_table = Table(
    'users',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),  # Первичный ключ, автоинкремент
    Column('telegram_id', Integer, unique=True),  # Идентификатор пользователя в Telegram
    Column('role_id', Integer, ForeignKey('roles.id')),  # Внешний ключ к таблице 'roles'
    Column('username', String(255), nullable=True),  # Имя пользователя
    Column('first_name', String(255), nullable=True),  # Имя
    Column('second_name', String(255), nullable=True),  # Фамилия
    Column('phone_number', String(255), nullable=True),  # Номер телефона
    Column('email', String(255), nullable=True),  # Электронная почта
    Column('avatar', String(255), nullable=True), # Аватарка пользователя
    Column('last_active', DateTime) # Поле для хранения времени последней активности
)

# Определение класса Role, связанного с таблицей 'roles'
class Role(Base):
    __table__ = roles_table

    id = roles_table.c.id
    name = roles_table.c.name
    permission = roles_table.c.permission

    # Опциональная связь с User
    users = relationship('User', backref='role')

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
    last_active = users_table.c.last_active

    # Связь с другими таблицами
    role = relationship(Role)  # Связь с объектом Role
