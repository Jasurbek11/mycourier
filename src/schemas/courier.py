from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from ..models.models import CourierStatus, DocumentStatus, TransportType, VehicleDocsStatus
import re
from .user import UserResponse
from enum import Enum

def validate_phone(v: str) -> str:
    if not re.match(r'^\+998\d{9}$', v):
        raise ValueError('Phone number must be in format +998XXXXXXXXX')
    return v

def validate_pinfl(v: str) -> str:
    if not re.match(r'^\d{14}$', v):
        raise ValueError('PINFL must be 14 digits')
    return v

class CourierBase(BaseModel):
    full_name: str
    phone: str
    pinfl: str
    transport_type: TransportType
    vehicle_number: Optional[str] = None
    vehicle_model: Optional[str] = None
    documents_status: Optional[DocumentStatus] = DocumentStatus.NOT_VERIFIED
    vehicle_docs_status: Optional[VehicleDocsStatus] = None

    @field_validator('phone')
    def validate_phone_field(cls, v):
        return validate_phone(v)

    @field_validator('pinfl')
    def validate_pinfl_field(cls, v):
        if not re.match(r'^\d{14}$', v):
            raise ValueError('ПИНФЛ должен содержать 14 цифр')
        return v

class TransportType(str, Enum):
    pedestrian = "pedestrian"
    bicycle = "bicycle"
    moto = "moto"
    auto = "auto"

class CourierCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(..., pattern=r'^\+998\d{9}$')
    pinfl: str = Field(..., pattern=r'^\d{14}$')
    transport_type: TransportType
    vehicle_number: Optional[str] = None
    vehicle_model: Optional[str] = None

    class Config:
        from_attributes = True

class CourierUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    pinfl: Optional[str] = None
    transport_type: Optional[str] = None
    onboarding_status: Optional[str] = None
    vehicle_number: Optional[str] = None
    vehicle_model: Optional[str] = None

    class Config:
        from_attributes = True

class CourierInDB(CourierBase):
    id: int
    status: CourierStatus
    documents_verified: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by_id: int
    updated_by_id: Optional[int] = None
    log_partner: str

    class Config:
        from_attributes = True

class CourierList(BaseModel):
    items: List[CourierInDB]
    total: int

class CourierResponse(BaseModel):
    id: int
    full_name: str
    phone: str
    pinfl: str
    status: str
    onboarding_status: str
    documents_status: str
    transport_type: str
    vehicle_number: Optional[str]
    vehicle_model: Optional[str]
    vehicle_docs_status: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    verified_at: Optional[datetime]
    verified_by: Optional[str]

    class Config:
        from_attributes = True