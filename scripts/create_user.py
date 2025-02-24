import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from src.database import SessionLocal
from src.models.models import User, UserRole, LogPartner
from src.models.auth import Auth

def create_onboarding_user():
    db = SessionLocal()
    try:
        user = User(
            username="onboarding",
            email="onboarding@example.com",
            hashed_password=Auth.get_password_hash("onboarding123"),
            role=UserRole.ONBOARDING,
            log_partner=LogPartner.DOSTAVLYAYU,
            is_active=True
        )
        db.add(user)
        db.commit()
        print("User created successfully!")
    except Exception as e:
        print(f"Error creating user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_onboarding_user()