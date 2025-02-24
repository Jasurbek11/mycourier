from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.models import User, UserRole  # Добавляем импорт UserRole
from src.models.auth import Auth
from src.config import get_settings

settings = get_settings()

def create_user(username: str, password: str, role: UserRole, email: str = None):
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Проверяем существование пользователя
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            print(f"User {username} already exists")
            return False
            
        # Создаем нового пользователя
        hashed_password = Auth.get_password_hash(password)
        new_user = User(
            username=username,
            hashed_password=hashed_password,
            email=email,
            role=role,
            is_active=True
        )
        db.add(new_user)
        db.commit()
        print(f"User {username} created successfully with role {role}")
        return True
    except Exception as e:
        print(f"Error creating user: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    # Создаем пользователя-онбордера
    username = "onboarder"
    password = "onboarder123"
    create_user(
        username=username,
        password=password,
        role=UserRole.ONBOARDING,
        email="onboarder@example.com"
    ) 