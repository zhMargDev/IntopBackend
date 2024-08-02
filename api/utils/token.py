from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from fastapi import HTTPException
import os
import config
from fastapi.responses import JSONResponse

# Конфигурация для JWT
SECRET_KEY = os.getenv("SECRET_KEY", config.SECRET_KEY)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 часа

# Метод для создания jwt токена
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Декодирование и возвращение user_id из токена
def decode_access_token(token: str):
    try:
        # Декодируем токен, чтобы получить полезную нагрузку (payload)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Проверка времени истечения срока действия токена
        exp = payload.get("exp")
        if exp is None:
            raise HTTPException(status_code=401, detail="Токен не содержит времени истечения")
        
        exp_datetime = datetime.fromtimestamp(exp)
        if datetime.now() > exp_datetime:
            raise HTTPException(status_code=401, detail="Токен истек")
        
        user_id = payload.get("sub")  # Извлекаем идентификатор пользователя
        if user_id is None:
            raise HTTPException(status_code=401, detail="Токен не содержит идентификатора пользователя")
        
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Токен истек")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Неверный токен")

# Функция для обновления токена и установки его в куки
def update_token(response: JSONResponse, user_id: int):
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = create_access_token(
        data={"sub": user_id}, expires_delta=access_token_expires
    )

    response.set_cookie(
        key="access_token",
        value=new_access_token,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Время действия куки в секундах
        httponly=True,  # Устанавливаем флаг, чтобы предотвратить доступ к куке через JavaScript
        secure=True,    # Устанавливаем флаг, чтобы кука передавалась только по HTTPS
        samesite="Lax"  # Политика кросс-сайтовых запросов
    )
    
    return response