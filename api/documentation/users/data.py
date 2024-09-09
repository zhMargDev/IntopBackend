"""
    В Этом файле храняться тексты документации, description для эндпоинтов

    Данные пользователя
"""

get_user_data = """
Этот эндпоинт возвращает все данные пользователя исходя из id указанный в куки
**Пример запроса**
curl -v -X POST "http://localhost:8000/users/my_data" \
-H "Content-Type: application/json" \
-b "access_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwiZXhwIjoxNzIzMzIyODMzfQ.1bwnUmgPwoo9AkT4eBU2P7aFAVPvnnfx_rCxtoyaceQ"

**Ответ:**
```
Если не было ошибки вернутся данные пользователя.
```
**Ошибки:**
```
- `200`: Всё прошло успешно, данные получены.
- `403`: Пользователь не найдено, удалён или токен не действителен.
- `500`: Произошла ошибка на сервере.
"""

update_user = """
Обновляет информацию о пользователе. Необходимо отправить форму с данными, которые требуется обновить.
При успешном обновлении возвращается сообщение об успешном обновлении.
**Параметры формы:**
- `user_id`: Id пользователя для проверки совместимости с токеном, если не отправить то вернёться ошибка
- `first_name`: Имя пользователя (опционально)
- `second_name`: Фамилия пользователя (опционально)
- `username`: Имя пользователя (опционально)
- `phone_number`: Номер телефона (опционально)
- `email`: Адрес электронной почты (опционально)
- `region_id`: Идентификатор региона (опционально)
- `avatar`: Новый аватар пользователя (опционально)
```
Пример Curl
curl -v -X PUT "http://localhost:8000/users/update" \
  -H "Content-Type: multipart/form-data" \
  -b "access_token=your_access_token" \
  -F "user_id"=1 \
  -F "first_name=John" \
  -F "second_name=Doe" \
  -F "username=johndoe" \
  -F "phone_number=1234567890" \
  -F "email=john.doe@example.com"
```
**Ответ:**
```
- Если обновление прошло успешно, возвращается сообщение о успешном обновлении данных.
```
**Ошибки:**
```
- `401 Unauthorized`: Токен доступа отсутствует или недействителен.
- `401 Unauthorized`: Недействительный пользователь. Отправленный id и id из токена не совпали или id не был отправлен.
- `404 Not Found`: Пользователь не найден.
"""

deactivate_user = """
Этот эндпоинт деактивирует аккаунт пользователя.
**Параметры запроса:**
- `user_id`: Идентификатор пользователя (необязательный параметр). Если не указан, то пользователь поддельный.
**Пример запроса**
curl -v -X DELETE "http://localhost:8000/users/deactivate" \
   -H "Content-Type: application/json" \
   -b "access_token=your_access_token" \
   -G \
   -d "user_id=1"
**Ответ:**
```
- Если деактивация успешна, возвращается сообщение о том, что аккаунт успешно деактивирован и токен доступа удаляется из куки.
- В случае отсутствия токена, его недействительности или несоответствия `user_id` возвращается ошибка.
```
**Ошибки:**
```
- `401 Unauthorized`: Токен доступа отсутствует, недействителен или `user_id` не совпадает.
- `404 Not Found`: Пользователь не найден.
"""

get_users_by_filters = """
Этот эндпоинт возвращает пользователей по указанным фильтрам.
Если фильтры не указаны, то вернутся все активные пользователи.
**Пример запроса**
```
curl -X GET "http://localhost:8000/users/by_filters?id=1&username=johndoe"
```
**Ответ:**
```
Если не было ошибки вернётся массив со всеми пользователями, соответствующими фильтрам, которые не удалили (деактивировали) свой аккаунт.
```
**Ошибки:**
```
- `200`: Всё прошло успешно, данные получены.
- `403`: Пользователей не найдено
- `500`: Произошла ошибка на сервере.
"""