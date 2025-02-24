from sqlalchemy.orm import Session
from ..models.models import Courier, CourierHistory, OnboardingStatus, CourierStatus, DocumentStatus
from ..schemas.courier import CourierCreate
from fastapi import HTTPException
import logging

async def create_courier(db: Session, courier_data: CourierCreate, current_user):
    try:
        # Проверяем, существует ли курьер с таким телефоном или ПИНФЛ
        existing_courier = db.query(Courier).filter(
            (Courier.phone == courier_data.phone) | 
            (Courier.pinfl == courier_data.pinfl)
        ).first()
        
        if existing_courier:
            if existing_courier.phone == courier_data.phone:
                raise HTTPException(
                    status_code=400,
                    detail="Курьер с таким номером телефона уже существует"
                )
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Курьер с таким ПИНФЛ уже существует"
                )

        # Создаем нового курьера
        courier = Courier(
            full_name=courier_data.full_name,
            phone=courier_data.phone,
            pinfl=courier_data.pinfl,
            transport_type=courier_data.transport_type,
            vehicle_number=courier_data.vehicle_number,
            vehicle_model=courier_data.vehicle_model,
            documents_status=courier_data.documents_status,
            vehicle_docs_status=courier_data.vehicle_docs_status,
            onboarding_status=OnboardingStatus.IN_PROGRESS,
            status=CourierStatus.INACTIVE,
            created_by_id=current_user.id,
            log_partner=current_user.log_partner
        )
        
        db.add(courier)
        db.commit()
        db.refresh(courier)
        
        # Добавляем запись в историю
        history = CourierHistory(
            courier_id=courier.id,
            type="onboarding",
            event="Создан новый курьер",
            status=OnboardingStatus.IN_PROGRESS,
            created_by_id=current_user.id
        )
        db.add(history)
        db.commit()
        
        return courier
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logging.error(f"Ошибка при создании курьера: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при создании курьера: {str(e)}"
        ) 