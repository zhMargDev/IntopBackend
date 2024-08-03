from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, MetaData, Table
from sqlalchemy.orm import declarative_base, relationship

# Создание экземпляра MetaData
metadata = MetaData()

# Создание базового класса с использованием декларативной базы
Base = declarative_base()

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
    Column('telegram_id', Integer, unique=True),
    Column('role_id', Integer, ForeignKey('roles.id')),
    Column('username', String(255), nullable=True),
    Column('first_name', String(255), nullable=True),
    Column('second_name', String(255), nullable=True),
    Column('phone_number', String(255), nullable=True),
    Column('email', String(255), nullable=True),
    Column('avatar', String(255), nullable=True),
    Column('rating', Float, nullable=True),
    Column('last_active', DateTime),
    Column('region_id', Integer, ForeignKey('regions.id'), nullable=True),
    Column('is_verified', Boolean, default=False),
    Column('is_active', Boolean, default=True)
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
    Column('address', String(255), nullable=True),
    Column('region_id', Integer, ForeignKey('regions.id'), nullable=True),
    Column('category_id', Integer, ForeignKey('categories.id'), nullable=False),
    Column('owner_id', Integer, ForeignKey('users.id')),
    Column('rating', Float, nullable=True),
    Column('is_verified', Boolean, default=False)
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
    rating = users_table.c.rating
    last_active = users_table.c.last_active
    region_id = users_table.c.region_id
    is_verified = users_table.c.is_verified
    is_active = users_table.c.is_active

    # Связь с другими таблицами
    role = relationship(Role, backref='users')
    region = relationship('Region', backref='users')

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
    parent = relationship('Category', remote_side=[categories_table.c.id], backref='children')

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

    # Связь с другими таблицами
    owner = relationship(User, backref='stores')
    category = relationship(Category, backref='stores')
    region = relationship('Region', backref='stores')

# Определение класса StoreEmail, связанного с таблицей 'store_emails'
class StoreEmail(Base):
    __table__ = store_emails_table

    id = store_emails_table.c.id
    store_id = store_emails_table.c.store_id
    email = store_emails_table.c.email
    email_type = store_emails_table.c.email_type

    # Связь с Store
    store = relationship(Store, backref='emails')

# Определение класса StorePhoneNumber, связанного с таблицей 'store_phone_numbers'
class StorePhoneNumber(Base):
    __table__ = store_phone_numbers_table

    id = store_phone_numbers_table.c.id
    store_id = store_phone_numbers_table.c.store_id
    phone_number = store_phone_numbers_table.c.phone_number
    phone_type = store_phone_numbers_table.c.phone_type

    # Связь с Store
    store = relationship(Store, backref='phone_numbers')

# Определение класса Region, связанного с таблицей 'regions'
class Region(Base):
    __table__ = regions_table

    id = regions_table.c.id
    name = regions_table.c.name
    parent_id = regions_table.c.parent_id

    # Связь с дочерними регионами
    parent = relationship('Region', remote_side=[regions_table.c.id], backref='children')
