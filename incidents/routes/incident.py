from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from schemas import *
from services import *

router = APIRouter(prefix="/incident")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/")
def report_incident(data: IncidentCreate, db: Session = Depends(get_db)):
    incident = create_incident(db, data)
    return {
        "success": True,
        "data": {"id": incident.id},
        "message": "Incident reported"
    }

@router.get("/")
def read_incidents(db: Session = Depends(get_db)):
    incidents = fetch_incidents(db)
    return {
        "success": True,
        "data": incidents,
        "message": "All incidents"
    }

@router.post("/update-status")
def update_status(data: IncidentStatusUpdate, db: Session = Depends(get_db)):
    incident = update_incident_status(db, data.incident_id, data.status)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    return {
        "success": True,
        "data": {"id": incident.id, "status": incident.status},
        "message": "Status updated"
    }
