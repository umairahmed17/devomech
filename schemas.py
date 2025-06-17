from pydantic import BaseModel, EmailStr
from typing import Optional, Literal, Dict
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
    status: Literal['active', 'inactive', 'maintenance']

    class Config:
        from_attributes = True

class DeviceStateUpdate(BaseModel):
    status: Literal['active', 'inactive', 'maintenance']

class TelemetryData(BaseModel):
    data: Dict
    device_id: int

class TelemetryResponse(BaseModel):
    id: int
    device_id: int
    timestamp: datetime
    data: Dict

    class Config:
        from_attributes = True

