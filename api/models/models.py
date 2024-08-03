from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, MetaData
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

# Определение таблицы 'users'
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

    # Связь с другими таблицами
    role = relationship('Role', back_populates='users')

# Определение таблицы 'ratings'
class Rating(Base):
    __tablename__ = 'ratings'
    id = Column(Integer, primary_key=True, autoincrement=True)
    rater_id = Column(Integer, nullable=False)
    rated_id = Column(Integer, nullable=False)
    rating = Column(Float, nullable=False)