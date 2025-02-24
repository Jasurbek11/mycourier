from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Dict
from ..database import get_db
from ..models.models import (
    Courier, CourierStatus, User, UserRole,
    DocumentStatus, TransportType
)
from ..schemas.courier import CourierCreate, CourierUpdate, CourierInDB
from .auth import get_current_user
from datetime import datetime

router = APIRouter()

@router.post("/activate/{courier_id}", response_model=Dict[str, str])
async def activate_courier(
    courier_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Активировать курьера"""
    current_user = await get_current_user(request, db)
    courier = db.query(Courier).filter(
        Courier.id == courier_id,
        Courier.log_partner == current_user.log_partner
    ).first()
    
    if not courier:
        raise HTTPException(status_code=404, detail="Courier not found")
    
    courier.status = CourierStatus.ACTIVE
    courier.updated_at = datetime.utcnow()
    db.commit()
    return {"message": "Courier activated successfully"}

@router.post("/deactivate/{courier_id}", response_model=Dict[str, str])
async def deactivate_courier(
    courier_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Деактивировать курьера"""
    current_user = await get_current_user(request, db)
    courier = db.query(Courier).filter(
        Courier.id == courier_id,
        Courier.log_partner == current_user.log_partner
    ).first()
    
    if not courier:
        raise HTTPException(status_code=404, detail="Courier not found")
    
    courier.status = CourierStatus.INACTIVE
    courier.updated_at = datetime.utcnow()
    db.commit()
    return {"message": "Courier deactivated successfully"}

@router.post("/{courier_id}/block", response_model=CourierInDB)
async def block_courier(
    courier_id: int,
    reason: Dict[str, str],
    db: Session = Depends(get_db)
):
    courier = db.query(Courier).filter(Courier.id == courier_id).first()
    if not courier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Courier not found"
        )
    
    courier.status = CourierStatus.BLOCKED
    # Здесь можно добавить логирование причины блокировки
    db.commit()
    db.refresh(courier)
    return courier

@router.post("/{courier_id}/fire", response_model=CourierInDB)
async def fire_courier(
    courier_id: int,
    reason: Dict[str, str],
    db: Session = Depends(get_db)
):
    courier = db.query(Courier).filter(Courier.id == courier_id).first()
    if not courier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Courier not found"
        )
    
    courier.status = CourierStatus.FIRED
    # Здесь можно добавить логирование причины увольнения
    db.commit()
    db.refresh(courier)
    return courier 