from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.models import Base, User, UserRole

# Создаем подключение к базе данных
SQLALCHEMY_DATABASE_URL = "sqlite:///./mycourier.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def update_user():
    db = SessionLocal()
    try:
        # Находим пользователя
        user = db.query(User).filter(User.username == "onboarder").first()
        if user:
            # Обновляем log_partner
            user.log_partner = "default"
            db.commit()
            print(f"Пользователь {user.username} обновлен. Log Partner: {user.log_partner}")
        else:
            print("Пользователь не найден")
    finally:
        db.close()

if __name__ == "__main__":
    update_user() 