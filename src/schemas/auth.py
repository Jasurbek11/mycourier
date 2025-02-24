from pydantic import BaseModel, EmailStr
from typing import Optional, Dict
from ..models.models import UserRole

class UserBase(BaseModel):
    id: int
    username: str
    role: str
    email: str

class Token(BaseModel):
    access_token: str
    token_type: str
    redirect_url: str
    user: Dict

class TokenData(BaseModel):
    user_id: int
    username: str

class UserAuth(BaseModel):
    username: str
    password: str

class UserCreate(UserAuth):
    email: EmailStr
    role: UserRole 