from fastapi import APIRouter
from .incident import router as incident_router
from .safety import router as safety_router

router = APIRouter()

router.include_router(incident_router, tags=["Incidents"])
router.include_router(safety_router, tags=["Safety"])
