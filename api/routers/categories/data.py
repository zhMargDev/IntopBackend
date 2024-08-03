from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from database import get_db
from models.models import Category
from models.schemas import CategoryOut

router = APIRouter()

# Роутер для получения всех категорий с их подкатегориями
@router.get('/all', response_model=List[CategoryOut],
            summary="Получение всех категгори и вложенных подкатегорий.",
            description="""
    Этот эндпоинт позволяет получить все категории и их подкатегории в виде иерархической структуры.

    **Запрос:**

    Отправьте GET-запрос на этот эндпоинт.

    **Ответ:**

    В случае успешного выполнения запроса вы получите JSON-ответ, содержащий все категории с их подкатегориями в следующем формате:

    ```json
    [
      {
        "id": 1,                       # Уникальный идентификатор категории
        "name": "Категория 1",         # Название категории
        "subcategories": [             # Список подкатегорий
          {
            "id": 2,
            "name": "Подкатегория 1.1",
            "subcategories": []         # Подкатегории подкатегории, если имеются
          }
        ]
      }
    ]
    ```

    **Статусные коды:**

    - **200 OK:** Категории и их подкатегории успешно получены.
    - **500 Internal Server Error:** Произошла ошибка на сервере при обработке запроса.

    **Примечания:**

    - Рекурсивное получение всех подкатегорий осуществляется для каждой категории.
    - Если в базе данных нет ни одной категории, ответ будет пустым массивом.
    """)
async def get_all_categories(db: AsyncSession = Depends(get_db)):
    async def fetch_categories(parent_id: int = None):
        query = select(Category).filter(Category.parent_id == parent_id)
        result = await db.execute(query)
        categories = result.scalars().all()
        result_list = []
        for category in categories:
            children = await fetch_categories(parent_id=category.id)
            result_list.append(CategoryOut(
                id=category.id,
                name=category.name,
                subcategories=children
            ))
        return result_list

    return await fetch_categories()

# Роутер для получения категории по id с её подкатегориями
@router.get('/by_id/{category_id}', response_model=CategoryOut,
            summary="Получение категории и его субкатегорий по id",
            description="""
    Этот эндпоинт позволяет получить категорию по её идентификатору и все её подкатегории.

    **Запрос:**

    Отправьте GET-запрос на этот эндпоинт с идентификатором категории в URL-параметре.

    **Параметры запроса:**
    - **category_id**: Идентификатор категории, которую нужно получить.

    **Ответ:**

    В случае успешного выполнения запроса вы получите JSON-ответ с данными категории и её подкатегориями в следующем формате:

    ```json
    {
      "id": 1,                       # Уникальный идентификатор категории
      "name": "Категория 1",         # Название категории
      "subcategories": [             # Список подкатегорий
        {
          "id": 2,
          "name": "Подкатегория 1.1",
          "subcategories": []         # Подкатегории подкатегории, если имеются
        }
      ]
    }
    ```

    **Статусные коды:**

    - **200 OK:** Категория и её подкатегории успешно получены.
    - **404 Not Found:** Категория с указанным идентификатором не найдена.
    - **500 Internal Server Error:** Произошла ошибка на сервере при обработке запроса.

    **Примечания:**

    - Если категория не найдена, будет возвращен статус 404 Not Found.
    - Рекурсивное получение всех подкатегорий осуществляется для указанной категории.
    """)
async def get_category_by_id(category_id: int, db: AsyncSession = Depends(get_db)):
    async def fetch_category_with_subcategories(category_id: int):
        query = select(Category).filter(Category.id == category_id)
        result = await db.execute(query)
        category = result.scalar_one_or_none()
        if not category:
            raise HTTPException(status_code=404, detail="Категория не найдена")
        
        subcategories = await fetch_categories(parent_id=category.id)
        return CategoryOut(
            id=category.id,
            name=category.name,
            subcategories=subcategories
        )

    async def fetch_categories(parent_id: int):
        query = select(Category).filter(Category.parent_id == parent_id)
        result = await db.execute(query)
        categories = result.scalars().all()
        result_list = []
        for category in categories:
            children = await fetch_categories(parent_id=category.id)
            result_list.append(CategoryOut(
                id=category.id,
                name=category.name,
                subcategories=children
            ))
        return result_list

    return await fetch_category_with_subcategories(category_id)