from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

class RegistrationData(BaseModel):
    date: date
    count: int

class StatsResponse(BaseModel):
    total_couriers: int = Field(default=0)
    active_couriers: int = Field(default=0)
    inactive_couriers: int = Field(default=0)
    blocked_couriers: int = Field(default=0)
    registrations: List[RegistrationData] = Field(default_factory=list)
    total_registrations: int = Field(default=0)

    class Config:
        from_attributes = True 