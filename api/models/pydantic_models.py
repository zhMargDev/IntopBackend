from pydantic import BaseModel

# Pydantic модель для получения данных
class TelegramInitData(BaseModel):
    id: int
    first_name: str
    last_name: str
    username: str