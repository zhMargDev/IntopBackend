from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from database import get_db
from models import User
from models.pydantic_models import TelegramInitData
from utils.token import update_token

router = APIRouter()

@router.post("/tg_authorization", summary="Авторизация через Telegram",
             description="""
             Этот эндпоинт обрабатывает авторизацию пользователей через Telegram. 
             Он получает информацию о пользователе из Telegram, обновляет или создает запись пользователя в базе данных, 
             управляет токенами доступа.

             **Запрос:**

             Отправьте POST-запрос на этот эндпоинт с JSON-данными в теле запроса:

             ```json
             {
               "id": 123456789,  # Telegram ID пользователя
               "first_name": "Иван",  # Имя пользователя
               "last_name": "Иванов",  # Фамилия пользователя
               "username": "ivan_ivanov"  # Username пользователя в Telegram
             }
             ```

             **Ответ:**

              В случае успешной авторизации вы получите JSON-ответ с токеном доступа, установленным в куке:

             ```json
             {
               "message": "Авторизация прошла успешно, токен доступа установлен в куке."
             }
             ```

             **Статусные коды:**

             - **200 OK:** Авторизация прошла успешно, токен доступа установлен в куке.
             - **400 Bad Request:** Неверный формат запроса.

             **Примечания:**

             - Если пользователь уже существует в базе данных, его информация будет обновлена предоставленными данными.
             - Если пользователь новый, будет создана новая запись пользователя.
             - Токены доступа действительны в течение 24 часов, при бездействии она будет удалено.
             """)
async def tg_authorization(init_data: TelegramInitData, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.telegram_id == str(init_data.id)).first()
    
    if user:
        user.first_name = init_data.first_name
        user.last_name = init_data.last_name
        user.username = init_data.username
        user.last_active = datetime.now()  # Обновляем время последнего действия
    else:
        user = User(
            telegram_id=str(init_data.id),
            first_name=init_data.first_name,
            last_name=init_data.last_name,
            username=init_data.username,
            last_active=datetime.now()  # Обновляем время последнего действия
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # Обновляем токен и устанавливаем его в куки
    response = JSONResponse(content={"message": "Авторизация прошла успешно, токен доступа установлен в куке."})
    response = update_token(response, user.id)
    
    return response