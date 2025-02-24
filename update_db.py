from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.models import (
    Base, User, UserRole, 
    CourierHistory, CourierStatusHistory, 
    CourierReferral, Equipment, EquipmentAssignment
)
from src.models.auth import Auth
from src.config import get_settings

settings = get_settings()

def update_database():
    # Создаем подключение к базе данных
    engine = create_engine(settings.DATABASE_URL)
    
    # Пересоздаем все таблицы
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    # Создаем сессию
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Создаем тестового пользователя
        hashed_password = Auth.get_password_hash("password123")
        test_user = User(
            username="Jas",
            email="jas@example.com",
            hashed_password=hashed_password,
            role=UserRole.ONBOARDING,
            is_active=True,
            log_partner="test_partner"
        )
        
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        print("\nБаза данных обновлена")
        print("Создан тестовый пользователь:")
        print(f"Username: {test_user.username}")
        print(f"Role: {test_user.role}")
        print(f"Log Partner: {test_user.log_partner}")
        print(f"Is active: {test_user.is_active}")
        
    except Exception as e:
        print(f"Ошибка: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_database() 