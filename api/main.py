import os

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse

from routers.users.auth import router as auth_router
from routers.users.data import router as data_router
from routers.users.rating import router as rating_router
from routers.categories.data import router as categories_router
from routers.stores.data import router as store_router
from routers.services.services import router as services_router
from routers.services.advertisements import router as advertisements_router

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

@app.get("/", tags=["Основная"], 
         summary="Основная информация для перехода в документацию.")
def read_item():
    return {"data": "Documentation is available at /docs"}

@app.get("/file/{folder}/{filename}",
         tags=["Получение картинок."],
         summary="Получение картинки по URL.",
         description="""
            Указывается URL адрес картинки к примеру <domain>/file/<папка>/<название картинки.расширение>.
            В ответе будет получена картинка.
        """)
async def get_image(folder: str, filename: str):
    # Формируем полный путь к файлу
    file_path = os.path.join("static", folder, filename)
    
    # Проверяем, существует ли файл
    if not os.path.exists(file_path):
        return Response(content="File not found", status_code=404)
    
    # Возвращаем файл как ответ
    return FileResponse(file_path)

# Авторизация
app.include_router(auth_router, prefix="/users", tags=["Авторизация"])
# Получение или изменения данных пользователей
app.include_router(data_router, prefix="/users", tags=["Пользователи"])
# Оценка пользователей
app.include_router(rating_router, prefix="/users", tags=["Рейтинг пользователей"])
# Категории
app.include_router(categories_router, prefix="/category", tags=["Категории"])
# Магазины
app.include_router(store_router, prefix="/stores", tags=["Магазины и компании"])
# Сервисы
app.include_router(services_router, prefix="/services", tags=["Сервисы"])
# Объявления сервисов
app.include_router(advertisements_router, prefix="/advertisements", tags=["Объявления сервисов"])
