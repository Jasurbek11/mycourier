from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.models import User
from src.config import get_settings

settings = get_settings()

def check_user(username: str):
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        user = db.query(User).filter(User.username == username).first()
        if user:
            print(f"User found: {user.username}, role: {user.role}")
        else:
            print(f"User {username} not found")
        return user
    finally:
        db.close() 