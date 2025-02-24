from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.models import User, UserRole
from src.models.auth import Auth
from src.config import get_settings

settings = get_settings()

def insert_user(username: str, password: str, email: str, role: UserRole):
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        hashed_password = Auth.get_password_hash(password)
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            role=role
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"User {username} inserted successfully")
        return user
    except Exception as e:
        print(f"Error inserting user: {str(e)}")
        db.rollback()
        return None
    finally:
        db.close()

if __name__ == "__main__":
    # Создаем подключение к базе данных
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # Удалим существующего пользователя с таким же именем, если он есть
        existing_user = db.query(User).filter(User.username == "Jas").first()
        if existing_user:
            db.delete(existing_user)
            db.commit()
            print("Существующий пользователь удален")

        # Создаем нового пользователя
        new_user = insert_user(
            username="Jas",
            password="123",
            email="onboarding@example.com",
            role=UserRole.ONBOARDING
        )
        
        # Проверяем созданного пользователя
        if new_user:
            print("\nИнформация о созданном пользователе:")
            print(f"Username: {new_user.username}")
            print(f"Email: {new_user.email}")
            print(f"Role: {new_user.role}")
            print(f"Is active: {new_user.is_active}")
            print(f"Hashed password: {new_user.hashed_password}")

            # Проверяем аутентификацию
            print("\nПроверка аутентификации:")
            is_valid = Auth.verify_password("123", new_user.hashed_password)
            print(f"Прямая проверка пароля: {'успешно' if is_valid else 'неуспешно'}")
    finally:
        db.close() 