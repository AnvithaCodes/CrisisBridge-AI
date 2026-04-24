from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import SessionLocal
import services
from schemas import IncidentCreate

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/get-incidents")
def read_incidents(db: Session = Depends(get_db)):
    return services.fetch_incidents(db)
