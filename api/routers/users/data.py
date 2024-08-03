from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Request, Query, Body
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models.models import User
from models.schemas import UserList, UserOut, UserUpdate, DeleteUserRequest
from utils.token import decode_access_token, update_token

router = APIRouter()

def handle_exception(exception):
    # Метод вывода ошибки 500
    raise HTTPException(status_code=500, detail=str(exception))

def update_last_active(user: User, db: Session):
    # Метод обновления последней активности для пользователя
    user.last_active = datetime.now()
    db.commit()

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
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="Токен доступа не предоставлен")

    try:
        user_id = decode_access_token(access_token)
        if not user_id:
            raise HTTPException(status_code=401, detail="Недействительный токен доступа")

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        update_last_active(user, db)
        response = UserOut.from_orm(user)
        response = update_token(request, response)

        return response

    except Exception as e:
        handle_exception(e)

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
        id: Optional[int] = Query(None),
        telegram_id: Optional[int] = Query(None),
        role_id: Optional[int] = Query(None),
        username: Optional[str] = Query(None),
        first_name: Optional[str] = Query(None),
        second_name: Optional[str] = Query(None),
        phone_number: Optional[str] = Query(None),
        email: Optional[str] = Query(None),
        rating: Optional[float] = Query(None),
        db: Session = Depends(get_db)
    ):
        try:
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

            query = db.query(User)
            for attr, value in filters.items():
                if value is not None:
                    query = query.filter(attr == value)

            users = query.all()
            if not users:
                raise HTTPException(status_code=403, detail="Пользователей не найдено")

            return UserList(users=[UserOut.from_orm(user) for user in users])

        except Exception as e:
            handle_exception(e)

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
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="Токен доступа не предоставлен")

    try:
        user_id = decode_access_token(access_token)
        if not user_id:
            raise HTTPException(status_code=401, detail="Недействительный токен доступа")

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        user_data = await request.json()
        update_data = UserUpdate(**user_data)
        for key, value in update_data.dict(exclude_unset=True).items():
            setattr(user, key, value)

        update_last_active(user, db)
        db.commit()  # Не забудьте зафиксировать изменения в базе данных

        # Обновите токен и добавьте его в куки
        response_data = {"message": "Данные пользователя обновлены"}
        new_token = update_token(request, response_data)  # Используем update_token для получения нового токена
        response = JSONResponse(content=response_data)
        response.set_cookie(key="access_token", value=new_token, httponly=True, secure=True)  # Устанавливаем новый токен в куки

        return response

    except Exception as e:
        handle_exception(e)

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
        users = db.query(User).all()
        return UserList(users=[UserOut.from_orm(user) for user in users])

    except Exception as e:
        handle_exception(e)

@router.post("/delete_user", summary="Удаление пользователя",
             description="""
             Этот эндпоинт позволяет удалить пользователя по указанному идентификатору.

             **Запрос:**

             Отправьте POST-запрос на этот эндпоинт с телом запроса в формате JSON, содержащим идентификатор пользователя и кукой, содержащей токен доступа.

             **Тело запроса:**

             ```json
             {
                 "user_id": 123
             }
             ```

             **Ответ:**

             В случае успешного выполнения запроса вы получите сообщение об успешном удалении пользователя.

             **Статусные коды:**

             - **200 OK:** Пользователь успешно удален.
             - **401 Unauthorized:** Токен доступа отсутствует или недействителен.
             - **404 Not Found:** Пользователь с указанным идентификатором не найден.
             """)
async def delete_user(request: Request, db: Session = Depends(get_db), body: DeleteUserRequest = Body(...)):
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="Токен доступа не предоставлен")

    try:
        admin_id = decode_access_token(access_token)
        if not admin_id:
            raise HTTPException(status_code=401, detail="Недействительный токен доступа")

        user = db.query(User).filter(User.id == body.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        db.delete(user)
        db.commit()

        # Удалите токен из куки
        response = JSONResponse(content={"message": "Пользователь удален"})
        response.set_cookie(key="access_token", value="", expires=0, httponly=True, secure=True)  # Удаляем токен из куки

        return response

    except Exception as e:
        handle_exception(e)

@router.post("/log_out", summary="Выход из аккаунта",
             description="Обновляет время последней активности пользователя и удаляет токен доступа из куки. "
                         "После выполнения этого запроса пользователь будет полностью разлогинен, и токен будет удален.")
async def log_out(request: Request, db: Session = Depends(get_db)):
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="Токен доступа не предоставлен")

    try:
        user_id = decode_access_token(access_token)
        if not user_id:
            raise HTTPException(status_code=401, detail="Недействительный токен доступа")

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        # Обновите время последней активности пользователя
        update_last_active(user, db)

        # Удалите токен из куки
        response = JSONResponse(content={"message": "Вы успешно вышли из аккаунта"})
        response.set_cookie(key="access_token", value="", expires=0, httponly=True, secure=True)

        return response

    except Exception as e:
        handle_exception(e)