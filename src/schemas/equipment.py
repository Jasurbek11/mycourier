from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from ..models.models import EquipmentType, EquipmentStatus

class EquipmentBase(BaseModel):
    name: str
    type: EquipmentType
    serial_number: str
    status: Optional[EquipmentStatus] = EquipmentStatus.AVAILABLE

class EquipmentCreate(EquipmentBase):
    pass

class EquipmentUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[EquipmentType] = None
    serial_number: Optional[str] = None
    status: Optional[EquipmentStatus] = None

class EquipmentInDB(EquipmentBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True 