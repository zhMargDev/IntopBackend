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

# Такблица способов оплаты
payment_methodes_table = Table(
    'payment_methodes',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('method_name', String(255))
)

# Таблица рейтинга объявления
ratings_table = Table(
    'ratings',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('advertisement_id', Integer, nullable=False),
    Column('rater_id', Integer, nullable=False)
)

# Таблица количество просмотров
views_table = Table(
    'views',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('advertisement_id', Integer, nullable=False),
    Column('rater_id', Integer, nullable=False)
)

# Таблица объявлений
advertisements_table = Table(
    'advertisements',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String(255), nullable=False),
    Column('location', String(255), nullable=False),
    Column('rating_count', Integer,  default=0, nullable=False),
    Column('views_count', Integer, default=0, nullable=False),
    Column('description', String(3000), nullable=True),
    Column('price', Integer, nullable=False),
    Column('owner_id', Integer, nullable=False),
    Column('is_active', Boolean, nullable=False, default=False),
    Column('timer', Integer, nullable=True, default=2592000), # 30 days timer until activation
    Column('picture', String(255), nullable=True),
    Column('service_id', Integer, ForeignKey('services.id'), nullable=False),
    Column('payment_method_id', Integer,  ForeignKey('payment_methodes.id'), nullable=True)
)
