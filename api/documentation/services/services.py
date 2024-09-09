get_all_services = """
Этот эндпоинт позволяет получить все сервисы или конкретный сервис по указанному id.

**Как можно запрос отправлять**:
- Для получения всех сервисов: `GET /services/all`
- Для получения конкретного сервиса по id: `GET /services/all?id=2`

**Какие параметры можно указать**:
- `id`: (необязательный) ID сервиса для фильтрации. Если указан, будет возвращен только сервис с этим ID.

**Пример ответа**:
```json
[
    {
        "id": 1,
        "title": "Сервис 1",
        "description": "Описание сервиса 1",
        "picture": "http://example.com/picture1.jpg"
    },
    {
        "id": 2,
        "title": "Сервис 2",
        "description": "Описание сервиса 2",
        "picture": "http://example.com/picture2.jpg"
    }
]
```

**Какие статус коды можно получить**:
- `200 OK`: Успешный запрос, возвращает список сервисов или один сервис.
- `404 Not Found`: Сервисы не найдены или указанный сервис не найден.
"""