import sys
import os
from pathlib import Path

# Добавляем путь к корневой директории проекта
project_root = str(Path(__file__).parent)
sys.path.append(project_root)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.models import Base, User, UserRole
from src.auth.auth import get_password_hash

# Создаем подключение к базе данных
SQLALCHEMY_DATABASE_URL = "sqlite:///./mycourier.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_onboarder():
    try:
        db = SessionLocal()
        
        # Проверяем существование пользователя
        existing_user = db.query(User).filter(User.username == "onboarder").first()
        if existing_user:
            print("Пользователь 'onboarder' уже существует")
            return
        
        # Создаем пользователя
        hashed_password = get_password_hash("onboarder123")
        user = User(
            username="onboarder",
            email="onboarder@example.com",
            hashed_password=hashed_password,
            role=UserRole.ONBOARDING,  # Используем enum
            is_active=True,
            log_partner="default"
        )
        
        db.add(user)
        db.commit()
        print("Пользователь 'onboarder' успешно создан")
        
    except Exception as e:
        print(f"Ошибка при создании пользователя: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    create_onboarder() 