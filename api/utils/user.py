from fastapi import HTTPException, Header

# Функция для получения текущего пользователя на основе токена авторизации
def get_current_user(authorization: str = Header(None)):
    # Проверка, что заголовок авторизации передан
    if not authorization:
        # Если заголовок не передан, выбрасываем ошибку с кодом 401 (Unauthorized)
        raise HTTPException(status_code=401, detail="Authorization header is missing")

    try:
        # Извлекаем токен из заголовка "Authorization". Ожидается, что он передан в формате "Bearer <id_token>"
        id_token = authorization.split(" ")[1]
        
        # Используем Firebase Admin SDK для проверки и декодирования токена
        decoded_token = auth.verify_id_token(id_token)
        
        # Получаем уникальный идентификатор пользователя (uid) из декодированного токена
        uid = decoded_token["uid"]
        
        # Возвращаем uid (идентификатор пользователя)
        return uid
    except Exception as e:
        # Если что-то пошло не так (например, неверный токен), выбрасываем ошибку с кодом 401 и соответствующим сообщением
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")