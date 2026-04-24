from pydantic import BaseModel

class IncidentCreate(BaseModel):
    title: str
    incident_type: str
    latitude: float
    longitude: float
    reporter_id: int

class IncidentStatusUpdate(BaseModel):
    incident_id: int
    status: str

class SafetyRequest(BaseModel):
    user_lat: float
    user_lon: float
