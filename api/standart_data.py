from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.models import Base, Role  # Импортируйте свои модели и Base из соответствующего модуля
from config import DB_CONNECT  # Импортируйте URL вашей базы данных

def roles():
    # Автозаполнение ролей
    # Создание подключения к базе данных
    engine = create_engine(DB_CONNECT)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Проверка наличия данных в таблице 'roles'
    if session.query(Role).count() == 0:
        # Определение начальных данных
        roles = [
            {"name": "admin", "permission": "all"},
            {"name": "user", "permission": "basic"},
            {"name": "guest", "permission": "read"}
        ]
        
        # Заполнение таблицы 'roles'
        for role_data in roles:
            role = Role(name=role_data["name"], permission=role_data["permission"])
            session.add(role)
        
        session.commit()
        print("Roles populated successfully.")
    else:
        print("Roles table already contains data.")

    session.close()

if __name__ == "__main__":
    roles()