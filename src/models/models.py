from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLAlchemyEnum, ForeignKey, Float
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
from ..database import Base
import enum
from datetime import datetime
from enum import Enum
from sqlalchemy.ext.declarative import declarative_base

# Экспортируем Base вместе с остальными моделями
__all__ = [
    "Base",
    "User", "UserRole",
    "Courier", "CourierStatus", "TransportType", "DocumentStatus", "VehicleDocsStatus",
    "Equipment", "EquipmentType", "EquipmentStatus",
    "EquipmentAssignment"
]

# Enums для User
class UserRole(str, Enum):
    ADMIN = "admin"
    ONBOARDING = "onboarding"
    OPERATOR = "operator"

# Enums для Courier
class TransportType(str, enum.Enum):
    PEDESTRIAN = "pedestrian"
    AUTO = "auto"
    BICYCLE = "bicycle"
    MOTO = "moto"

class CourierStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BLOCKED = "blocked"
    FIRED = "fired"

class DocumentStatus(str, Enum):
    NOT_VERIFIED = 'NOT_VERIFIED'
    VERIFIED = 'VERIFIED'
    PROBLEM = 'PROBLEM'

# Enums для Equipment
class EquipmentType(str, enum.Enum):
    PHONE = "phone"
    TABLET = "tablet"
    SCANNER = "scanner"
    OTHER = "other"

class EquipmentStatus(str, enum.Enum):
    AVAILABLE = "available"
    ASSIGNED = "assigned"
    MAINTENANCE = "maintenance"
    BROKEN = "broken"

class OnboardingStatus(str, Enum):
    WILL_BE_VERIFIED = 'WILL_BE_VERIFIED'  # Оформится
    VERIFIED = 'VERIFIED'                   # Оформлен
    REJECTED_BY_HUB = 'REJECTED_BY_HUB'     # Отказ хаба
    REJECTED_BY_COURIER = 'REJECTED_BY_COURIER' # Отказ курьера

    @classmethod
    def from_string(cls, value):
        try:
            return cls(value)
        except ValueError:
            if value == 'IN_PROGRESS':
                return cls.WILL_BE_VERIFIED
            raise

class VehicleDocsStatus(str, Enum):
    NOT_VERIFIED = 'NOT_VERIFIED'
    VERIFIED = 'VERIFIED'
    PROBLEM = 'PROBLEM'

# Models
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(200))
    role = Column(String(50))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    log_partner = Column(String(50))
    region_id = Column(Integer, ForeignKey('regions.id'), nullable=True)

    region = relationship('Region', foreign_keys=[region_id])

    def to_dict(self):
        """Преобразование объекта в словарь"""
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role,
            "email": self.email,
            "is_active": self.is_active
        }

class Courier(Base):
    __tablename__ = "couriers"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    phone = Column(String, unique=True, nullable=False)
    pinfl = Column(String, unique=True, nullable=False)
    status = Column(SQLAlchemyEnum(CourierStatus), default=CourierStatus.INACTIVE)
    onboarding_status = Column(SQLAlchemyEnum(OnboardingStatus), default=OnboardingStatus.WILL_BE_VERIFIED)
    documents_status = Column(SQLAlchemyEnum(DocumentStatus), default=DocumentStatus.NOT_VERIFIED)
    transport_type = Column(SQLAlchemyEnum(TransportType))
    vehicle_number = Column(String, nullable=True)
    vehicle_model = Column(String, nullable=True)
    vehicle_docs_status = Column(SQLAlchemyEnum(VehicleDocsStatus), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = Column(Integer, ForeignKey("users.id"))
    updated_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    verified_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    verified_at = Column(DateTime, nullable=True)
    log_partner = Column(String, nullable=True)

    # Отношения
    created_by = relationship("User", foreign_keys=[created_by_id])
    verified_by = relationship("User", foreign_keys=[verified_by_id])
    history = relationship("CourierHistory", back_populates="courier")
    equipment_assignments = relationship("EquipmentAssignment", back_populates="courier")

    # Разрешаем любое изменение статуса
    @validates('onboarding_status')
    def validate_onboarding_status(self, key, value):
        if isinstance(value, OnboardingStatus):
            return value
        if isinstance(value, str):
            return OnboardingStatus[value.upper()]
        raise ValueError(f"Invalid onboarding status: {value}")

class Equipment(Base):
    __tablename__ = "equipment"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    type = Column(SQLAlchemyEnum(EquipmentType))
    serial_number = Column(String, unique=True)
    status = Column(SQLAlchemyEnum(EquipmentStatus), default=EquipmentStatus.AVAILABLE)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    assignments = relationship("EquipmentAssignment", back_populates="equipment")

class EquipmentAssignment(Base):
    __tablename__ = "equipment_assignments"

    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id"))
    courier_id = Column(Integer, ForeignKey("couriers.id"))
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    returned_at = Column(DateTime(timezone=True), nullable=True)
    condition_on_return = Column(SQLAlchemyEnum(EquipmentStatus), nullable=True)
    notes = Column(String)

    # Relationships
    equipment = relationship("Equipment", back_populates="assignments")
    courier = relationship("Courier", back_populates="equipment_assignments")

class CourierHistory(Base):
    __tablename__ = "courier_history"

    id = Column(Integer, primary_key=True, index=True)
    courier_id = Column(Integer, ForeignKey("couriers.id"))
    type = Column(String)  # onboarding, activation, service, warehouse, payment
    event = Column(String)
    status = Column(String, nullable=True)
    comment = Column(String, nullable=True)
    documents_status = Column(SQLAlchemyEnum(DocumentStatus), nullable=True)
    amount = Column(Float, nullable=True)
    reason = Column(String, nullable=True)
    equipment_name = Column(String, nullable=True)
    created_by_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    courier = relationship("Courier", back_populates="history")
    created_by = relationship("User")

class CourierStatusHistory(Base):
    __tablename__ = "courier_status_history"

    id = Column(Integer, primary_key=True, index=True)
    courier_id = Column(Integer, ForeignKey("couriers.id"))
    status = Column(SQLAlchemyEnum(CourierStatus))
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    reason = Column(String, nullable=True)
    courier_id_by_activator = Column(String, nullable=True)  # ID курьера от активатора

    # Relationships
    courier = relationship("Courier", backref="status_history")
    user = relationship("User")

class CourierReferral(Base):
    __tablename__ = "courier_referrals"

    id = Column(Integer, primary_key=True, index=True)
    referrer_id = Column(Integer, ForeignKey("couriers.id"))
    referred_id = Column(Integer, ForeignKey("couriers.id"))
    status = Column(String)  # PENDING, APPROVED, REJECTED, PAID
    bonus_amount = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    confirmed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    confirmed_at = Column(DateTime, nullable=True)

    # Relationships
    referrer = relationship("Courier", foreign_keys=[referrer_id], backref="referrals_made")
    referred = relationship("Courier", foreign_keys=[referred_id], backref="referral_info")
    confirmed_by = relationship("User")

class Region(Base):
    __tablename__ = 'regions'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    code = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)