from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from ..models.models import EquipmentStatus

class EquipmentBase(BaseModel):
    name: str
    serial_number: str
    status: EquipmentStatus

class EquipmentCreate(EquipmentBase):
    pass

class EquipmentUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[EquipmentStatus] = None

class EquipmentInDB(EquipmentBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class EquipmentAssignmentBase(BaseModel):
    courier_id: int
    notes: Optional[str] = None

class EquipmentAssignmentCreate(EquipmentAssignmentBase):
    pass

class EquipmentAssignmentReturn(BaseModel):
    condition_on_return: EquipmentStatus
    notes: Optional[str] = None

class EquipmentAssignmentInDB(EquipmentAssignmentBase):
    id: int
    equipment_id: int
    assigned_at: datetime
    returned_at: Optional[datetime] = None
    condition_on_return: Optional[EquipmentStatus] = None

    class Config:
        from_attributes = True 