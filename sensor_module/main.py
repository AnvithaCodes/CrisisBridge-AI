"""
Sensor Module — Standalone FastAPI Application
================================================
Runs COMPLETELY ISOLATED on port 8001 to avoid any conflict
with the main CrisisBridge app on port 8000.

How to run:
    uvicorn sensor_module.main:app --reload --port 8001

Swagger UI available at:
    http://localhost:8001/docs
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sensor_module.api.routes import router
from sensor_module.core.sensor_manager import seed_demo_sensors

# ── Create App ───────────────────────────────────────
app = FastAPI(
    title="CrisisBridge — Sensor Module",
    version="1.0.0",
    description=(
        "Live Sensor Simulation & Alert Pre-Processor. "
        "Isolated module — runs on port 8001. "
        "Detects anomalous spikes and triggers admin alerts."
    ),
)

# ── CORS (allow frontend demo panel) ─────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Open for demo; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register Routes ──────────────────────────────────
app.include_router(router)


# ── Startup Event ────────────────────────────────────
@app.on_event("startup")
def on_startup():
    """Seed demo sensors so the system is not empty on first launch."""
    seed_demo_sensors()
    print("✅ Sensor Module started — 3 demo sensors pre-loaded.")
    print("📡 Swagger UI available at: http://localhost:8001/docs")


# ── Health Check ─────────────────────────────────────
@app.get("/health", tags=["Health"])
def health():
    """Health check for the sensor module."""
    return {"status": "ok", "module": "sensor_module", "port": 8001}
