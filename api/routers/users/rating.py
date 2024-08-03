from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from typing import Dict

from database import get_db
from models.models import User, Rating

router = APIRouter()

@router.post("/rate", summary="Оценить пользователя",
             description="""
             Этот эндпоинт позволяет пользователю оценивать другого пользователя в системе.

             **Запрос:**

             Отправьте POST-запрос на этот эндпоинт с параметрами:
             
             - `rater_id` (int): ID пользователя, который оставляет оценку.
             - `rated_id` (int): ID пользователя, который получает оценку.
             - `rating` (float): Оценка, выставляемая пользователем. Должна быть в диапазоне от 1 до 5.

             Пример тела запроса:
             
             ```json
             {
               "rater_id": 123,
               "rated_id": 456,
               "rating": 4.5
             }
             ```

             **Ответ:**

             В случае успешного выполнения запроса вы получите JSON-ответ с сообщением об успешном добавлении оценки и обновлении рейтинга пользователя:

             ```json
             {
               "message": "Rating added and user rating updated successfully"
             }
             ```

             Если оценка находится вне допустимого диапазона (менее 1 или более 5), вы получите ошибку 400 с описанием проблемы. Если один из пользователей не найден, вы получите ошибку 404.

             **Статусные коды:**

             - **200 OK:** Оценка успешно добавлена и рейтинг пользователя обновлен.
             - **400 Bad Request:** Оценка вне допустимого диапазона (1-5).
             - **404 Not Found:** Один или оба пользователя не найдены.
             """)
async def rate_user(rater_id: int, rated_id: int, rating: float, db: AsyncSession = Depends(get_db)) -> Dict[str, str]:
    # Проверка валидности рейтинга
    if rating < 1 or rating > 5:
        raise HTTPException(status_code=400, detail="Оценка должна быть от 1 до 5")

    # Проверка существования пользователя, который оставляет оценку
    rater = await db.execute(select(User).filter(User.id == rater_id))
    rater = rater.scalar_one_or_none()
    if rater is None:
        raise HTTPException(status_code=404, detail="Пользователь, оставляющий оценку, не найден.")

    # Проверка существования пользователя, которого оценивают
    rated = await db.execute(select(User).filter(User.id == rated_id))
    rated = rated.scalar_one_or_none()
    if rated is None:
        raise HTTPException(status_code=404, detail="Пользователь, который получает оценку, не найден.")

    # Добавление рейтинга
    new_rating = Rating(rater_id=rater_id, rated_id=rated_id, rating=rating)
    async with db.begin():
        db.add(new_rating)

    # Расчет средней оценки для оцененного пользователя
    avg_rating = await db.execute(select(func.avg(Rating.rating)).filter(Rating.rated_id == rated_id))
    avg_rating = avg_rating.scalar_one_or_none()
    
    # Обновление средней оценки пользователя в таблице 'users'
    if avg_rating is not None:  # Проверка на случай, если нет рейтингов
        async with db.begin():
            await db.execute(
                select(User).filter(User.id == rated_id).update({User.rating: avg_rating})
            )
    else:
        raise HTTPException(status_code=404, detail="Пользователь не найден.")

    return {"message": "Пользователь успешно оценён."}