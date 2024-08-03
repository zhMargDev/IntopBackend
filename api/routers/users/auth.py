from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from database import get_db
from models.models import User, Role
from models.schemas import TelegramInitData
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

             Curl запрос

             ```
             curl -X POST "http://<your_domain>/tg_authorization" \
             -H "Content-Type: application/json" \
             -d '{
                   "id": 123456789,
                   "first_name": "Иван",
                   "last_name": "Иванов",
                   "username": "ivan_ivanov"
                 }'

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
    # Поиск пользователя по Telegram ID
    user = db.query(User).filter(User.telegram_id == str(init_data.id)).first()
    
    if user:
        # Обновление информации о существующем пользователе
        user.first_name = init_data.first_name
        user.second_name = init_data.last_name
        user.username = init_data.username
        user.last_active = datetime.now()  # Обновляем время последнего действия

        # Проверка и обновление состояния is_active
        if not user.is_active:
            user.is_active = True

        db.commit()
        db.refresh(user)
    else:
        # Создание нового пользователя
        user = User(
            telegram_id=str(init_data.id),
            first_name=init_data.first_name,
            second_name=init_data.last_name,
            username=init_data.username,
            last_active=datetime.now(),  # Обновляем время последнего действия
            is_active=True  # Устанавливаем is_active в True для нового пользователя
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # Обновляем токен и устанавливаем его в куки
    response = JSONResponse(content={"message": "Авторизация прошла успешно, токен доступа установлен в куке."})
    response = update_token(response, user.id)
    
    return response