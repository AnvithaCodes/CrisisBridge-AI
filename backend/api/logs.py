"""
Logs API Routes for CrisisBridge AI
====================================
Endpoints:
- GET    /queries   — Get AI query logs (admin)
- DELETE /queries   — Clear all query logs (admin)
- GET    /incidents — Get incident history logs (admin)
- DELETE /incidents — Clear all incident logs (admin)
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from shared.dependencies import get_db, require_role
from shared.models import QueryLog, Incident, User
from shared.enums import UserRole

router = APIRouter()


@router.get(
    "/queries",
    summary="Get AI query logs (Admin only)"
)
async def get_query_logs(
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """
    Returns the most recent AI assistant queries and responses.
    """
    logs = db.query(QueryLog).order_by(QueryLog.created_at.desc()).limit(limit).all()
    return [
        {
            "id": log.id,
            "original_query": log.original_query,
            "rewritten_query": log.rewritten_query,
            "answer": log.answer,
            "confidence": log.confidence,
            "cache_status": log.cache_status.value if log.cache_status else "miss",
            "response_time_ms": round(log.response_time_ms, 0) if log.response_time_ms else None,
            "session_id": log.session_id,
            "created_at": log.created_at.isoformat() if log.created_at else None,
        }
        for log in logs
    ]


@router.delete(
    "/queries",
    summary="Clear all AI query logs (Admin only)"
)
async def clear_query_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """
    (Admin) Permanently deletes all query logs from the database.
    """
    deleted = db.query(QueryLog).delete()
    db.commit()
    return {"status": "CLEARED", "deleted_count": deleted}


@router.get(
    "/incidents",
    summary="Get incident history logs (Admin only)"
)
async def get_incident_logs(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """
    Returns a history of all incidents reported in the system.
    """
    return db.query(Incident).order_by(Incident.reported_at.desc()).limit(limit).all()


@router.delete(
    "/incidents",
    summary="Clear all incident history logs (Admin only)"
)
async def clear_incident_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """
    (Admin) Permanently deletes all incident logs from the database.
    """
    deleted = db.query(Incident).delete()
    db.commit()
    return {"status": "CLEARED", "deleted_count": deleted}
