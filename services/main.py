import os

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse

from routers.services.data import router as services_data

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
    return {"data": "Documentation is available at /docs"}

@app.get("/file/{folder}/{filename}")
async def get_image(folder: str, filename: str):
    # Формируем полный путь к файлу
    file_path = os.path.join("static", folder, filename)
    
    # Проверяем, существует ли файл
    if not os.path.exists(file_path):
        return Response(content="File not found", status_code=404)
    
    # Возвращаем файл как ответ
    return FileResponse(file_path)

# Сервисы
app.include_router(services_data, prefix="/services", tags=["services"])

# Монтируем статическую директорию, где будут храниться картинки
app.mount("/static", StaticFiles(directory="static"), name="static")
