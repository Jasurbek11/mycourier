from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime
from ..models.models import UserRole

class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: UserRole
    log_partner: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True,
        use_enum_values=True  # Это заставит Pydantic использовать значения enum вместо объектов
    )

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None

class UserInDB(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool = True

    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True,
        use_enum_values=True
    )

class Token(BaseModel):
    access_token: str
    token_type: str

class UserInfo(UserBase):
    id: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

class UserProfile(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    
    class Config:
        from_attributes = True

class UserInDB(UserBase):
    id: int
    is_active: bool = True
    log_partner: Optional[str] = None

    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    log_partner: Optional[str]

    class Config:
        from_attributes = True 