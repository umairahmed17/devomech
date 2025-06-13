from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict
from datetime import datetime

class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True

class DeviceBase(BaseModel):
    name: str
    location: Optional[str] = None

class DeviceCreate(DeviceBase):
    pass

class DeviceResponse(DeviceBase):
    id: int
    status: Dict

    class Config:
        from_attributes = True

class DeviceStateUpdate(BaseModel):
    status: Dict

class TelemetryData(BaseModel):
    data: Dict

class TelemetryResponse(BaseModel):
    id: int
    device_id: int
    timestamp: datetime
    data: Dict

    class Config:
        from_attributes = True

