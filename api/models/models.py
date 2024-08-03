from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, MetaData, Boolean
from sqlalchemy.orm import declarative_base, relationship

# Создание базового класса с использованием декларативной базы
Base = declarative_base()

# Определение таблицы 'roles'
class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    permission = Column(String(255), nullable=False)

    # Опциональная связь с User
    users = relationship('User', backref='role')

# Обновление таблицы 'users'
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(Integer, unique=True)
    role_id = Column(Integer, ForeignKey('roles.id'))
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    second_name = Column(String(255), nullable=True)
    phone_number = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    avatar = Column(String(255), nullable=True)
    rating = Column(Float, nullable=True)
    last_active = Column(DateTime)
    region_id = Column(Integer, ForeignKey('regions.id'), nullable=True)  # Регион пользователя
    is_verified = Column(Boolean, default=False)  # Флаг подтверждения пользователя

    # Связь с другими таблицами
    role = relationship('Role', back_populates='users')
    region = relationship('Region', backref='users')

# Определение таблицы 'ratings'
class Rating(Base):
    __tablename__ = 'ratings'
    id = Column(Integer, primary_key=True, autoincrement=True)
    rater_id = Column(Integer, nullable=False)
    rated_id = Column(Integer, nullable=False)
    rating = Column(Float, nullable=False)

# Определение таблицы 'categories' бесконечной вложенности
class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    parent_id = Column(Integer, ForeignKey('categories.id'), nullable=True)

    # Опциональная связь с родительской категорией
    parent = relationship('Category', remote_side=[id], backref='children')

# Обновление таблицы 'stores'
class Store(Base):
    __tablename__ = 'stores'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    short_name = Column(String(100), nullable=False)
    llc_name = Column(String(255), nullable=True)
    address = Column(String(255), nullable=True)
    region_id = Column(Integer, ForeignKey('regions.id'), nullable=True)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    owner_id = Column(Integer, ForeignKey('users.id'))
    rating = Column(Float, nullable=True)  # Поле рейтинга
    is_verified = Column(Boolean, default=False)

    owner = relationship('User', backref='owned_stores')
    category = relationship('Category', backref='stores')
    region = relationship('Region', backref='stores')

# Определение таблицы 'store_emails' эл. почты магазина с объяснением что это за майл
class StoreEmail(Base):
    __tablename__ = 'store_emails'
    id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(Integer, ForeignKey('stores.id'))  # Магазин, к которому относится email
    email = Column(String(255), nullable=False)  # Email адрес
    email_type = Column(String(50), nullable=False)  # Тип email (например, 'support', 'info', 'sales')

    # Связь с магазином
    store = relationship('Store', backref='emails')

# Определение таблицы 'store_phone_numbers' номеров теефонов магазина с объясненеием что это за номер
class StorePhoneNumber(Base):
    __tablename__ = 'store_phone_numbers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(Integer, ForeignKey('stores.id'))  # Магазин, к которому относится номер
    phone_number = Column(String(20), nullable=False)  # Номер телефона
    phone_type = Column(String(50), nullable=False)  # Тип номера (например, 'support', 'sales', 'fax')

    # Связь с магазином
    store = relationship('Store', backref='phone_numbers')

# Определение таблицы 'regions' бесконечной вложенности
class Region(Base):
    __tablename__ = 'regions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    parent_id = Column(Integer, ForeignKey('regions.id'), nullable=True)

    # Опциональная связь с родительской областью
    parent = relationship('Region', remote_side=[id], backref='children')

