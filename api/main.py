from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.users.auth import router as auth_router
from routers.users.data import router as data_router
from routers.users.rating import router as rating_router
from routers.categories.data import router as categories_router
from routers.stores.data import router as stores_router

app = FastAPI()

# Настройка CORS
origins = [
    "https://intop.uz",
    "http://localhost",
    "http://localhost:8000",  # Порт по умолчанию для FastAPI
    "http://localhost:8080",  # Порт по умолчанию для Vue js
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Позволяет все HTTP-методы
    allow_headers=["*"],  # Позволяет все заголовки
)

@app.get("/", summary="Main info")
def read_item():
    return {"data": "Hello"}

# Авторизация
app.include_router(auth_router, prefix="/users", tags=["users"])
# Получение или изменения данных пользователей
app.include_router(data_router, prefix="/users", tags=["users"])
# Оценка пользователей
app.include_router(rating_router, prefix="/users", tags=["users_rating"])
# Категории
app.include_router(categories_router, prefix="/category", tags=["categories"])
# Магазины
app.include_router(stores_router, prefix="/store", tags=["stores"])