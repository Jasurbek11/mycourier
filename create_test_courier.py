from sqlalchemy.orm import Session
from src.database import SessionLocal, engine
from src.models.models import Courier, OnboardingStatus, CourierStatus, DocumentStatus, TransportType
from datetime import datetime

def create_test_courier():
    db = SessionLocal()
    try:
        # Создаем тестового курьера
        courier = Courier(
            full_name="Jasurbek Khudayberganov",
            phone="+998999662906",
            pinfl="51807056520030",
            status=CourierStatus.INACTIVE,
            onboarding_status=OnboardingStatus.IN_PROGRESS,
            documents_status=DocumentStatus.NOT_VERIFIED,
            transport_type=TransportType.PEDESTRIAN,
            log_partner='default',
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(courier)
        db.commit()
        db.refresh(courier)
        print(f"Created test courier with ID: {courier.id}")
        
    except Exception as e:
        print(f"Error creating test courier: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_courier() 