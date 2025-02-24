from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.models import User, UserRole
from src.models.auth import Auth
from src.config import get_settings
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

def create_user(username: str, password: str, email: str, role: UserRole):
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Проверка на существующего пользователя
        existing_user = db.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            logger.warning(f"User with username {username} or email {email} already exists")
            return None
            
        hashed_password = Auth.get_password_hash(password)
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            role=role,
            is_active=True  # Явно устанавливаем активный статус
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"User {username} created successfully with role {role}")
        return user
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        db.rollback()
        return None
    finally:
        db.close()

if __name__ == "__main__":
    # Создаем тестового пользователя
    test_user = create_user(
        username="Jas",
        password="password123",
        email="jas@example.com",
        role=UserRole.ONBOARDING
    )
    if test_user:
        logger.info(f"\nСоздан тестовый пользователь:")
        logger.info(f"ID: {test_user.id}")
        logger.info(f"Username: {test_user.username}")
        logger.info(f"Role: {test_user.role}")
        logger.info(f"Is active: {test_user.is_active}") 