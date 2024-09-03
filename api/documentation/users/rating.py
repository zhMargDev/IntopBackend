"""
    В Этом файле храняться тексты документации, description для эндпоинтов

    Рейтинг пользователя
"""

rate_user = """
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
             """