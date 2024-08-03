from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Request, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from database import get_db
from models.models import User
from utils.token import decode_access_token, update_token

router = APIRouter()

@router.get("/user_data", summary="Получение данных пользователя",
            description="""
            Этот эндпоинт позволяет получить данные о текущем авторизованном пользователе, используя токен доступа, хранящийся в куках.

            **Запрос:**

            Отправьте GET-запрос на этот эндпоинт с кукой, содержащей токен доступа.

            **Ответ:**

            В случае успешного выполнения запроса вы получите JSON-ответ с данными пользователя:

            ```json
            {
              "user_id": 123456,           # Уникальный идентификатор пользователя
              "telegram_id": 987654321,   # Идентификатор пользователя в Telegram
              "role_id": 1,               # Идентификатор роли пользователя
              "username": "ivan_ivanov",  # Имя пользователя в системе
              "first_name": "Иван",       # Имя пользователя
              "second_name": "Иванов",    # Фамилия пользователя
              "phone_number": "+1234567890",  # Номер телефона пользователя
              "email": "ivan@example.com",   # Электронная почта пользователя
              "avatar": "path/to/avatar.jpg",  # Путь к аватарке пользователя
              "rating": 1-5, # Рейтинга пользователя
              "last_active": "2024-08-02T12:34:56"  # Время последней активности пользователя
            }
            ```

            **Статусные коды:**

            - **200 OK:** Данные пользователя успешно получены и возвращены.
            - **401 Unauthorized:** Токен доступа отсутствует или недействителен.
            - **404 Not Found:** Пользователь с указанным идентификатором не найден.

            **Примечания:**

            - Если токен доступа отсутствует или недействителен, будет возвращен статус 401 Unauthorized.
            - Если пользователь не найден, будет возвращен статус 404 Not Found.
            - При успешном запросе токен доступа будет обновлен, и новый токен будет установлен в куки.
            """)
async def get_user_data(request: Request, db: Session = Depends(get_db)):
    # Получаем токен доступа из куков
    access_token = request.cookies.get("access_token")
    
    if not access_token:
        # Если токен отсутствует, возвращаем ошибку 401 Unauthorized
        raise HTTPException(status_code=401, detail="Токен доступа не предоставлен")

    try:
        # Декодируем токен для получения идентификатора пользователя
        user_id = decode_access_token(access_token)
        
        if not user_id:
            # Если токен недействителен, возвращаем ошибку 401 Unauthorized
            raise HTTPException(status_code=401, detail="Недействительный токен доступа")

        # Находим пользователя по идентификатору
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            # Если пользователь не найден, возвращаем ошибку 404 Not Found
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        # Обновляем время последней активности пользователя
        user.last_active = datetime.now()
        db.commit()

        # Формируем ответ с данными пользователя
        response = JSONResponse(content={
            "user_id": user.id,
            "telegram_id": user.telegram_id,
            "role_id": user.role_id,
            "username": user.username,
            "first_name": user.first_name,
            "second_name": user.last_name,
            "phone_number": user.phone_number,
            "email": user.email,
            "avatar": user.avatar,
            "rating": user.rating,
            "last_active": user.last_active.isoformat()
        })

        # Обновляем токен и куку
        response = update_token(response, user.id)

        return response

    except HTTPException as e:
        # Передаем HTTP исключение дальше
        raise e
    except Exception as e:
        # Возвращаем ошибку 401 Unauthorized при возникновении исключения
        raise HTTPException(status_code=401, detail="Ошибка при декодировании токена или получении данных пользователя")

@router.get("/get_users_by", summary="Получение пользователей по параметрам",
            description="""
            Этот эндпоинт позволяет получить данные пользователей по различным параметрам. Вы можете отправить запрос с параметрами, такими как id, name, phone_number и другие, чтобы найти конкретного пользователя.

            **Запрос:**

            Отправьте GET-запрос на этот эндпоинт с параметрами запроса, например: ?id=1 или ?name=иван или ?id=2&phone_number=+134567890&name=иван.
            Ключи для запроса:
                id: int
                telegram_id: int
                role_id: int
                username: str
                first_name: str
                second_name: str
                phone_number: str
                email: str
            Примечание: Можно поставить несколько ключей с значением
            **Ответ:**

            В случае успешного выполнения запроса вы получите JSON-ответ с данными пользователей.

            ```json
            [
                {
                  "user_id": 123456,           # Уникальный идентификатор пользователя
                  "telegram_id": 987654321,   # Идентификатор пользователя в Telegram
                  "role_id": 1,               # Идентификатор роли пользователя
                  "username": "ivan_ivanov",  # Имя пользователя в системе
                  "first_name": "Иван",       # Имя пользователя
                  "second_name": "Иванов",    # Фамилия пользователя
                  "phone_number": "+1234567890",  # Номер телефона пользователя
                  "email": "ivan@example.com",   # Электронная почта пользователя
                  "avatar": "path/to/avatar.jpg",  # Путь к аватарке пользователя
                  "rating": 1-5, # Рейтинга пользователя
                  "last_active": "2024-08-02T12:34:56"  # Время последней активности пользователя
                },
                {...},
                {...}
            ]
            ```

            **Статусные коды:**

            - **200 OK:** Данные пользователей успешно получены.
            - **403 Forbidden:** Пользователей не было найдено по указанным параметрам.
            - **500 Internal Server Error:** Ошибка при получении данных о пользователях.
            """)
async def get_users_by(
    id: int = Query(None),
    telegram_id: int = Query(None),
    role_id: int = Query(None),
    username: str = Query(None),
    first_name: str = Query(None),
    second_name: str = Query(None),
    phone_number: str = Query(None),
    email: str = Query(None),
    rating: float = Query(None),
    db: Session = Depends(get_db)
):
    try:
        query = db.query(User)

        filters = {
            User.id: id,
            User.telegram_id: telegram_id,
            User.role_id: role_id,
            User.username: username,
            User.first_name: first_name,
            User.second_name: second_name,
            User.phone_number: phone_number,
            User.email: email,
            User.rating: rating
        }

        for attr, value in filters.items():
            if value is not None:
                query = query.filter(attr == value)

        users = query.all()

        if not users:
            raise HTTPException(status_code=403, detail="Пользователей не найден.")

        return JSONResponse(content=[{
            "user_id": user.id,
            "telegram_id": user.telegram_id,
            "role_id": user.role_id,
            "username": user.username,
            "first_name": user.first_name,
            "second_name": user.second_name,
            "phone_number": user.phone_number,
            "email": user.email,
            "avatar": user.avatar,
            "rating": user.rating,
            "last_active": user.last_active.isoformat()
        } for user in users])

    except Exception:
        raise HTTPException(status_code=500, detail="Ошибка при получении данных о пользователях")

@router.put("/update_user", summary="Обновление данных пользователя",
            description="""
            Этот эндпоинт позволяет обновить данные текущего авторизованного пользователя. 

            **Запрос:**

            Отправьте PUT-запрос на этот эндпоинт с кукой, содержащей токен доступа, и JSON-данными для обновления.

            **Ответ:**

            В случае успешного выполнения запроса вы получите сообщение об успешном обновлении данных пользователя.

            **Статусные коды:**

            - **200 OK:** Данные пользователя успешно обновлены.
            - **401 Unauthorized:** Токен доступа отсутствует или недействителен.
            - **404 Not Found:** Пользователь с указанным идентификатором не найден.
            - **400 Bad Request:** Неверные данные для обновления.
            """)
async def update_user(request: Request, db: Session = Depends(get_db)):
    # Получаем токен доступа из куков
    access_token = request.cookies.get("access_token")
    user_data = await request.json()

    if not access_token:
        # Если токен отсутствует, возвращаем ошибку 401 Unauthorized
        raise HTTPException(status_code=401, detail="Токен доступа не предоставлен")

    try:
        # Декодируем токен для получения идентификатора пользователя
        user_id = decode_access_token(access_token)
        
        if not user_id:
            # Если токен недействителен, возвращаем ошибку 401 Unauthorized
            raise HTTPException(status_code=401, detail="Недействительный токен доступа")

        # Находим пользователя по идентификатору
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            # Если пользователь не найден, возвращаем ошибку 404 Not Found
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        # Обновляем данные пользователя
        for key, value in user_data.items():
            setattr(user, key, value)
        
        # Обновляем время последней активности пользователя
        user.last_active = datetime.now()
        db.commit()

        return JSONResponse(content={"message": "Данные пользователя обновлены"})

    except HTTPException as e:
        # Передаем HTTP исключение дальше
        raise e
    except Exception as e:
        # Возвращаем ошибку 400 Bad Request при возникновении исключения
        raise HTTPException(status_code=400, detail="Ошибка при обновлении данных пользователя")

@router.get("/all_users", summary="Получение всех пользователей",
            description="""
            Этот эндпоинт позволяет получить список всех пользователей в системе.

            **Запрос:**

            Отправьте GET-запрос на этот эндпоинт.

            **Ответ:**

            В случае успешного выполнения запроса вы получите JSON-ответ со списком всех пользователей:

            ```json
            [
              {
                "user_id": 123456,
                "telegram_id": 987654321,
                "role_id": 1,
                "username": "ivan_ivanov",
                "first_name": "Иван",
                "second_name": "Иванов",
                "phone_number": "+1234567890",
                "email": "ivan@example.com",
                "avatar": "path/to/avatar.jpg",
                "rating": 1-5, # Рейтинга пользователя
                "last_active": "2024-08-02T12:34:56"
              },
              ...
            ]
            ```

            **Статусные коды:**

            - **200 OK:** Список пользователей успешно получен.
            - **500 Internal Server Error:** Ошибка при получении данных о пользователях.
            """)
async def get_all_users(db: Session = Depends(get_db)):
    try:
        # Получаем всех пользователей из базы данных
        users = db.query(User).all()
        return JSONResponse(content=[{
            "user_id": user.id,
            "telegram_id": user.telegram_id,
            "role_id": user.role_id,
            "username": user.username,
            "first_name": user.first_name,
            "second_name": user.last_name,
            "phone_number": user.phone_number,
            "email": user.email,
            "avatar": user.avatar,
            "rating": user.rating,
            "last_active": user.last_active.isoformat()
        } for user in users])
    except Exception as e:
        # Возвращаем ошибку 500 Internal Server Error при возникновении исключения
        raise HTTPException(status_code=500, detail="Ошибка при получении данных о пользователях")

@router.delete("/delete_user/{user_id}", summary="Удаление пользователя",
               description="""
               Этот эндпоинт позволяет удалить пользователя по указанному идентификатору.

               **Запрос:**

               Отправьте DELETE-запрос на этот эндпоинт с идентификатором пользователя в пути и кукой, содержащей токен доступа.

               **Ответ:**

               В случае успешного выполнения запроса вы получите сообщение об успешном удалении пользователя.

               **Статусные коды:**

               - **200 OK:** Пользователь успешно удален.
               - **401 Unauthorized:** Токен доступа отсутствует или недействителен.
               - **404 Not Found:** Пользователь с указанным идентификатором не найден.
               """)
async def delete_user(user_id: int, request: Request, db: Session = Depends(get_db)):
    # Получаем токен доступа из куков
    access_token = request.cookies.get("access_token")

    if not access_token:
        # Если токен отсутствует, возвращаем ошибку 401 Unauthorized
        raise HTTPException(status_code=401, detail="Токен доступа не предоставлен")

    try:
        # Декодируем токен для получения идентификатора пользователя
        admin_id = decode_access_token(access_token)
        
        if not admin_id:
            # Если токен недействителен, возвращаем ошибку 401 Unauthorized
            raise HTTPException(status_code=401, detail="Недействительный токен доступа")

        # Находим пользователя по идентификатору
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            # Если пользователь не найден, возвращаем ошибку 404 Not Found
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        # Удаляем пользователя
        db.delete(user)
        db.commit()

        return JSONResponse(content={"message": "Пользователь удален"})

    except HTTPException as e:
        # Передаем HTTP исключение дальше
        raise e
    except Exception as e:
        # Возвращаем ошибку 500 Internal Server Error при возникновении исключения
        raise HTTPException(status_code=500, detail="Ошибка при удалении пользователя")