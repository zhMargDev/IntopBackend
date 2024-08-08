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
    Column('telegram_id', Integer, unique=True),
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
    Column('last_active', DateTime),
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