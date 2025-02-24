import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.database import SessionLocal
from src.models.models import User, UserRole
from src.models.auth import Auth

def create_test_users():
    db = SessionLocal()
    
    test_users = [
        {
            "username": "owner",
            "email": "owner@mycourier.com",
            "password": "owner123",
            "role": UserRole.OWNER
        },
        {
            "username": "manager",
            "email": "manager@mycourier.com",
            "password": "manager123",
            "role": UserRole.MANAGER
        },
        {
            "username": "onboarding",
            "email": "onboarding@mycourier.com",
            "password": "onboarding123",
            "role": UserRole.ONBOARDING
        },
        {
            "username": "warehouse",
            "email": "warehouse@mycourier.com",
            "password": "warehouse123",
            "role": UserRole.WAREHOUSE
        },
        {
            "username": "security",
            "email": "security@mycourier.com",
            "password": "security123",
            "role": UserRole.SECURITY
        }
    ]

    for user_data in test_users:
        if not db.query(User).filter(User.username == user_data["username"]).first():
            hashed_password = Auth.get_password_hash(user_data["password"])
            user = User(
                username=user_data["username"],
                email=user_data["email"],
                hashed_password=hashed_password,
                role=user_data["role"]
            )
            db.add(user)
            print(f"Created user: {user_data['username']} with role {user_data['role']}")

    db.commit()
    db.close()

if __name__ == "__main__":
    create_test_users() 