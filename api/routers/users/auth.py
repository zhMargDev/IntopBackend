from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from database import get_db
from models.models import User, Role
from schemas.user import TelegramInitData, UserResponse
from utils.token import decode_access_token, update_token

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

             Curl

             ```
             curl -v -X POST "http://localhost:8000/users/tg_authorization" -H "Content-Type: application/json" -d '{                                                                                                                    
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
            created_at=datetime.now(),  # Добавляет дату создания аккаунта
            is_active=True  # Устанавливаем is_active в True для нового пользователя
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # Переоброзование времени последней активности в строку для передачи через json
    user.last_active = user.last_active.isoformat()
    # Создаем ответ с использованием UserResponse
    user_response = UserResponse.from_orm(user)

    # Обновляем токен и устанавливаем его в куки
    response = JSONResponse(content=user_response.dict())
    response = update_token(response, user.id)
    
    return response

@router.post('/my_data', summary="Получени данных пользователя",
    description="""
        Этот эндпоинт возвращает все данные пользователя исходя из id указанный в куки

        **Пример запроса**
        curl -v -X POST "http://localhost:8000/users/my_data" \
           -H "Content-Type: application/json" \
           -b "access_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwiZXhwIjoxNzIzMzIyODMzfQ.1bwnUmgPwoo9AkT4eBU2P7aFAVPvnnfx_rCxtoyaceQ"
        
        **Ответ:**
        Если не было ошибки вернутся данные пользователя.
        
        **Ошибки:**
        - `200`: Всё прошло успешно, данные получены.
        - `403`: Пользователь не найдено, удалён или токен не действителен.
        - `500`: Произошла ошибка на сервере.
    """)
async def get_my_data(request: Request, db: Session = Depends(get_db)):
    # Извлечение токена из куки
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=403, detail="Токен доступа отсутствует")

    # Получение user_id из токена
    try:
        payload = decode_access_token(token)
        token_user_id = int(payload['sub'])
    except HTTPException:
        raise HTTPException(status_code=403, detail="Недействительный токен")
    
    user = db.query(User).first()

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Пользователя не существует")

    # Устанавливаем время последней активности пользователя
    user.last_active = datetime.now()

    db.commit()
    db.refresh(user)

    # Переоброзование времени последней активности и даты создания в строку для передачи через json ! не сохраняем в базе
    user.last_active = user.last_active.isoformat()
    user.created_at = user.created_at.isoformat()

    # Создаем ответ с использованием UserResponse
    user_response = UserResponse.from_orm(user)

    # Обновляем токен и устанавливаем его в куки
    response = JSONResponse(content=user_response.dict())
    response = update_token(response, user.id)
    
    return response