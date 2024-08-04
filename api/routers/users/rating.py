from fastapi import APIRouter, HTTPException, Depends, Request
from starlette.responses import JSONResponse
from sqlalchemy.orm import Session

from database import get_db
from models.models import User, Rating
from models.schemas import RatingCreate
from utils.token import decode_access_token, update_token

router = APIRouter()



def update_average_rating(user_id: int, db: Session):
    # Получение всех рейтингов для указанного пользователя
    ratings = db.query(Rating).filter(Rating.rated_id == user_id).all()

    if not ratings:
        average_rating = None  # Или любое значение по умолчанию
    else:
        # Вычисление средней оценки
        average_rating = sum(rating.rating for rating in ratings) / len(ratings)

    # Обновление средней оценки пользователя
    user = db.query(User).filter(User.id == user_id).first()

    if user:
        user.rating = average_rating
        db.commit()

@router.post("/rate", summary="Оценка или изменение оценки пользователя",
             description="""
             Позволяет пользователю оценить другого пользователя или изменить ранее оставленную оценку.
             
             **Необходимо отправить:**
             - `rater_id`: ID пользователя, который оставляет оценку.
             - `rated_id`: ID пользователя, которого оценивают.
             - `rating`: Оценка, которую ставит пользователь (например, от 1 до 5).

             **Пример Curl:**
             ```
             curl -v -X POST "http://localhost:8000/users/rate" \
               -H "Content-Type: application/json" \
               -b "access_token=your_access_token" \
               -d '{"rater_id": 1, "rated_id": 1, "rating": 5}'
             ```

             **Ответ:**
             - `message`: Сообщение о результате операции ("Оценка пользователя обновлена" или "Пользователь оценен").

             **Ошибки:**
             - `401 Unauthorized`: Токен доступа отсутствует или недействителен.
             - `403 Forbidden`: Неправильный оценивающий пользователь, неправильный оценивающийся пользователь, или попытка оценить самого себя.
             """)
async def rate_user(
        request: Request,
        rating_data: RatingCreate,
        db: Session = Depends(get_db)
    ):
    # Извлечение токена из куки
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=401, detail="Токен доступа отсутствует")

    # Получение user_id из токена
    try:
        payload = decode_access_token(token)
        token_user_id = int(payload['sub'])
    except HTTPException:
        raise HTTPException(status_code=401, detail="Недействительный токен")

    # Проверка существования rater и rated пользователей
    rater = db.query(User).filter(User.id == rating_data.rater_id).first()
    rated = db.query(User).filter(User.id == rating_data.rated_id).first()

    if not rater or rater.id != token_user_id:
        raise HTTPException(status_code=403, detail="Неправильный оценивающий пользователь")

    if not rated:
        raise HTTPException(status_code=403, detail="Неправильный оценивающийся пользователь")

    if rater.id == rated.id:
        raise HTTPException(status_code=403, detail="Вы не можете оценить самого себя")


    # Проверка на существование рейтинга от данного rater для данного rated
    existing_rating = db.query(Rating).filter(
        Rating.rater_id == rating_data.rater_id,
        Rating.rated_id == rating_data.rated_id
    ).first()

    if existing_rating:
        # Обновление существующего рейтинга
        existing_rating.rating = rating_data.rating
        db.commit()
        message = "Оценка пользователя обнавлена"
    else:
        # Создание нового рейтинга
        new_rating = Rating(
            rater_id=rating_data.rater_id,
            rated_id=rating_data.rated_id,
            rating=rating_data.rating
        )
        db.add(new_rating)
        db.commit()
        message = "Пользователь оценён"

    # Обновление средней оценки пользователя
    update_average_rating(rating_data.rated_id, db)

    # Обновляем токен и устанавливаем его в куки
    response = JSONResponse(content={"message": message})
    response = update_token(response, rater.id)
    return response
