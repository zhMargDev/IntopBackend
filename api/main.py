from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.users.auth import router as auth_router
from routers.users.data import router as data_router

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

# Роутеры
app.include_router(auth_router, prefix="/users", tags=["users"])
app.include_router(data_router, prefix="/users", tags=["users"])