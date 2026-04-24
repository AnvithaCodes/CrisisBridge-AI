from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Sensor(BaseModel):
    sensor_id: str
    type: str  # fire, smoke, gas, water
    zone: str  # floor_3_kitchen
    threshold: float
    is_active: bool = True

class SensorReading(BaseModel):
    sensor_id: str
    value: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class SensorAlert(BaseModel):
    sensor_id: str
    type: str
    zone: str
    value: float
    threshold: float
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
