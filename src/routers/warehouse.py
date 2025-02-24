from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.models import (
    Equipment, EquipmentType, EquipmentStatus,
    EquipmentAssignment, User, UserRole, Courier, CourierStatus
)
from ..schemas.equipment import EquipmentCreate, EquipmentUpdate, EquipmentInDB
from .auth import get_current_user
from ..schemas.warehouse import (
    EquipmentAssignmentCreate,
    EquipmentAssignmentReturn,
    EquipmentAssignmentInDB
)
from datetime import datetime

router = APIRouter()

@router.post("/equipment/", response_model=EquipmentInDB)
async def create_equipment(
    equipment: EquipmentCreate,
    db: Session = Depends(get_db)
):
    db_equipment = Equipment(**equipment.dict())
    db.add(db_equipment)
    try:
        db.commit()
        db.refresh(db_equipment)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Equipment with this serial number already exists"
        )
    return db_equipment

@router.post("/equipment/{equipment_id}/assign", response_model=EquipmentAssignmentInDB)
async def assign_equipment(
    equipment_id: int,
    assignment: EquipmentAssignmentCreate,
    db: Session = Depends(get_db)
):
    # Проверяем существование оборудования
    equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found"
        )
    
    # Проверяем существование и статус курьера
    courier = db.query(Courier).filter(Courier.id == assignment.courier_id).first()
    if not courier or courier.status != CourierStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Courier not found or not active"
        )
    
    # Проверяем, не выдано ли уже оборудование
    existing_assignment = db.query(EquipmentAssignment).filter(
        EquipmentAssignment.equipment_id == equipment_id,
        EquipmentAssignment.returned_at.is_(None)
    ).first()
    
    if existing_assignment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Equipment is already assigned"
        )
    
    db_assignment = EquipmentAssignment(
        equipment_id=equipment_id,
        courier_id=assignment.courier_id,
        notes=assignment.notes
    )
    
    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)
    return db_assignment

@router.post("/equipment/{equipment_id}/return", response_model=EquipmentAssignmentInDB)
async def return_equipment(
    equipment_id: int,
    return_info: EquipmentAssignmentReturn,
    db: Session = Depends(get_db)
):
    # Находим активную выдачу оборудования
    assignment = db.query(EquipmentAssignment).filter(
        EquipmentAssignment.equipment_id == equipment_id,
        EquipmentAssignment.returned_at.is_(None)
    ).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active assignment found for this equipment"
        )
    
    # Обновляем запись о возврате
    assignment.returned_at = datetime.utcnow()
    assignment.condition_on_return = return_info.condition_on_return
    assignment.notes = return_info.notes
    
    # Обновляем статус оборудования
    equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    equipment.status = return_info.condition_on_return
    
    db.commit()
    db.refresh(assignment)
    return assignment 