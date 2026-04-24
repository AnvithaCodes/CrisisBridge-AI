from sqlalchemy.orm import Session
from shared.models import Incident
from shared.enums import IncidentStatus, IncidentType

def fetch_incidents(db: Session):
    return db.query(Incident).all()

def create_incident(db: Session, incident_data):
    # Map string type to Enum
    try:
        itype = IncidentType(incident_data.incident_type.lower())
    except ValueError:
        itype = IncidentType.OTHER

    new_incident = Incident(
        title=incident_data.title,
        incident_type=itype,
        latitude=incident_data.latitude,
        longitude=incident_data.longitude,
        status=IncidentStatus.REPORTED,
        reporter_id=incident_data.reporter_id
    )
    db.add(new_incident)
    db.commit()
    db.refresh(new_incident)
    return new_incident

def get_active_incidents(db: Session):
    return db.query(Incident).filter(
        Incident.status != IncidentStatus.RESOLVED,
        Incident.status != IncidentStatus.CLOSED
    ).all()

def update_incident_status(db: Session, incident_id: int, status_str: str):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        return None

    try:
        new_status = IncidentStatus(status_str.lower())
        incident.status = new_status
        db.commit()
        db.refresh(incident)
    except ValueError:
        pass # Handle invalid status if needed
        
    return incident
