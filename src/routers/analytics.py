from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict
from datetime import datetime, timedelta
from ..database import get_db
from ..models.models import Courier, CourierStatus, Equipment, EquipmentAssignment

router = APIRouter()

@router.get("/couriers/stats")
async def get_courier_stats(
    start_date: datetime = None,
    end_date: datetime = None,
    db: Session = Depends(get_db)
):
    query = db.query(Courier)
    
    if start_date and end_date:
        query = query.filter(Courier.created_at.between(start_date, end_date))
    
    stats = {
        "total": query.count(),
        "active": query.filter(Courier.status == CourierStatus.ACTIVE).count(),
        "inactive": query.filter(Courier.status == CourierStatus.INACTIVE).count(),
        "blocked": query.filter(Courier.status == CourierStatus.BLOCKED).count(),
        "fired": query.filter(Courier.status == CourierStatus.FIRED).count(),
    }
    
    return stats

@router.get("/equipment/stats")
async def get_equipment_stats(db: Session = Depends(get_db)):
    total_assignments = db.query(EquipmentAssignment).count()
    active_assignments = db.query(EquipmentAssignment)\
        .filter(EquipmentAssignment.returned_at.is_(None))\
        .count()
    
    return {
        "total_assignments": total_assignments,
        "active_assignments": active_assignments,
        "available_equipment": db.query(Equipment).count() - active_assignments
    } 