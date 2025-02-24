from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.models import Base, User, Courier, UserRole
import sys
from pathlib import Path

# Добавляем путь к корневой директории проекта
project_root = str(Path(__file__).parent)
sys.path.append(project_root)

# Создаем подключение к базе данных
SQLALCHEMY_DATABASE_URL = "sqlite:///./mycourier.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def check_database():
    db = SessionLocal()
    try:
        # Проверяем пользователей
        print("\nПользователи:")
        users = db.query(User).all()
        for user in users:
            print(f"""
User ID: {user.id}
Username: {user.username}
Role: {user.role}
Log Partner: {user.log_partner}
Is Active: {user.is_active}
            """)

        # Проверяем курьеров
        print("\nКурьеры:")
        couriers = db.query(Courier).all()
        for courier in couriers:
            print(f"""
Courier ID: {courier.id}
Name: {courier.full_name}
Phone: {courier.phone}
PINFL: {courier.pinfl}
Log Partner: {courier.log_partner}
Status: {courier.status}
Onboarding Status: {courier.onboarding_status}
Created By: {courier.created_by_id}
Created At: {courier.created_at}
            """)

    finally:
        db.close()

if __name__ == "__main__":
    check_database() 