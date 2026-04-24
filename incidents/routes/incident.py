from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from shared.dependencies import get_db
from ..schemas import IncidentCreate, IncidentStatusUpdate
from ..services import create_incident, fetch_incidents, update_incident_status
from shared.enums import IncidentStatus

router = APIRouter()

@router.post("/report")
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
    active_count = len([i for i in incidents if i.status not in [IncidentStatus.RESOLVED, IncidentStatus.CLOSED]])
    return {
        "success": True,
        "incidents": incidents,
        "active_count": active_count,
        "resolved_today": 0, # Placeholder for now
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
