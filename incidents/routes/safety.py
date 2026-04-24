from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from shared.dependencies import get_db
from ..services import get_active_incidents
from ..schemas import SafetyRequest
from shared.utils import calculate_distance_meters, determine_safety_level

router = APIRouter()

# Using shared get_db dependency

@router.post("/safety-check")
def safety_check(req: SafetyRequest, db: Session = Depends(get_db)):
    incidents = get_active_incidents(db)

    if not incidents:
        return {
            "success": True,
            "data": {"status": "SAFE"},
            "message": "No active incidents"
        }

    min_dist = float("inf")
    nearest = None

    for inc in incidents:
        dist = calculate_distance_meters(req.user_lat, req.user_lon, inc.latitude, inc.longitude)
        if dist < min_dist:
            min_dist = dist
            nearest = inc

    safety_status = determine_safety_level(min_dist)
    status = safety_status.value

    return {
        "success": True,
        "data": {
            "status": status,
            "nearest_distance_km": round(min_dist / 1000, 2),
            "nearest_incident": {
                "id": nearest.id,
                "type": nearest.incident_type.value
            }
        },
        "message": "Safety evaluated"
    }
