# models.py

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

SCHEMA = 'iot'

class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'schema': SCHEMA}

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default='user')

    devices = relationship("Device", back_populates="owner")

class Device(Base):
    __tablename__ = 'devices'
    __table_args__ = {'schema': SCHEMA}

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey(f'{SCHEMA}.users.id'))  # Schema-qualified
    location = Column(String)
    status = Column(JSON)

    owner = relationship("User", back_populates="devices")
    telemetries = relationship("Telemetry", back_populates="device")

class Telemetry(Base):
    __tablename__ = 'telemetries'
    __table_args__ = {'schema': SCHEMA}

    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey(f'{SCHEMA}.devices.id'))  # Schema-qualified
    timestamp = Column(DateTime, default=datetime.utcnow)
    data = Column(JSON)

    device = relationship("Device", back_populates="telemetries")

