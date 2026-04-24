"""
Sensor Module API Routes
=========================
All endpoints for the isolated sensor module.
Runs as a standalone FastAPI app on port 8001.

⚠️  ALL endpoints are ADMIN-ONLY in production.
    Add Depends(get_current_admin_user) once auth is integrated.

Endpoints:
  POST   /sensor/register       — Register a new sensor (admin)
  GET    /sensor/list           — List all registered sensors (admin)
  DELETE /sensor/{sensor_id}    — Remove a sensor (admin)
  POST   /sensor/data           — Submit a reading (simulator only)
  GET    /sensor/latest-readings — View last 20 readings (admin)
  GET    /sensor/alerts         — View recent spike alerts (admin)
  POST   /sensor/queue-spike    — Queue a controlled spike (admin/demo)
  GET    /sensor/queue-status   — View pending spike queue (admin)
"""

from fastapi import APIRouter, HTTPException
from typing import List

from sensor_module.models.sensor_model import Sensor, SensorReading, SensorAlert
from sensor_module.core import sensor_manager, spike_detector
from sensor_module.core.spike_queue import queue_spike, consume_spike, get_queue_status
from sensor_module.core.reading_log import log_reading, get_recent_readings

router = APIRouter(prefix="/sensor", tags=["Sensor Module"])


# ── Register a new sensor ─────────────────────────────
@router.post("/register", response_model=Sensor, summary="Register a new sensor")
def register_sensor(sensor: Sensor):
    """
    Registers a sensor with a custom threshold.
    Admin defines: sensor_id, type, zone, threshold.
    """
    existing = sensor_manager.get_sensor(sensor.sensor_id)
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Sensor '{sensor.sensor_id}' already registered. Use a unique sensor_id."
        )
    return sensor_manager.register_sensor(sensor)


# ── List all sensors ──────────────────────────────────
@router.get("/list", response_model=List[Sensor], summary="List all registered sensors (admin)")
def list_sensors():
    """(Admin) Returns all currently registered sensors."""
    return sensor_manager.list_sensors()

# ── Clear recent alerts ───────────────────────────────
@router.delete("/alerts", summary="Clear all recent spike alerts (admin)")
def delete_alerts():
    """
    (Admin) Clears the in-memory log of recent spike alerts.
    """
    spike_detector.clear_alerts()
    return {"status": "ALERTS_CLEARED", "message": "All alerts have been cleared."}


# ── Remove a sensor ───────────────────────────────────
@router.delete("/{sensor_id}", summary="Remove a sensor (admin)")
def delete_sensor(sensor_id: str) -> dict:
    """
    (Admin) Permanently removes a sensor from the in-memory registry.
    The simulator will stop including it in the live stream automatically.
    """
    removed = sensor_manager.remove_sensor(sensor_id)
    if not removed:
        raise HTTPException(
            status_code=404,
            detail=f"Sensor '{sensor_id}' not found."
        )
    return {"status": "REMOVED", "sensor_id": sensor_id}


# ── Submit a sensor reading (INTERNAL — simulator only) ──
@router.post("/data", include_in_schema=False)
def submit_reading(reading: SensorReading) -> dict:
    """Internal endpoint used only by the simulator. Hidden from Swagger."""
    sensor = sensor_manager.get_sensor(reading.sensor_id)
    if not sensor:
        raise HTTPException(
            status_code=404,
            detail=f"Sensor '{reading.sensor_id}' not found. Register it first."
        )

    # ── Spike Queue Check (consumed here, fires exactly once) ──
    # If an admin has queued a spike for this sensor, override the
    # incoming value to force a reading above the threshold.
    if consume_spike(reading.sensor_id):
        reading.value = sensor.threshold + 20.0  # Guaranteed spike

    alert = spike_detector.detect_spike(sensor, reading.value)

    if alert:
        log_reading(reading, "SPIKE_DETECTED")
        return {"status": "SPIKE_DETECTED", "alert": alert.dict()}

    log_reading(reading, "NORMAL")
    return {
        "status": "NORMAL",
        "sensor_id": reading.sensor_id,
        "value": reading.value,
        "message": "Value is within normal range."
    }


# ── View recent alerts ────────────────────────────────
@router.get("/alerts", response_model=List[SensorAlert], summary="Get recent spike alerts")
def get_alerts():
    """
    Returns the last 100 spike alerts (most recent first).
    In production: restrict this to admin users only.
    """
    return spike_detector.get_recent_alerts()


# ── View ALL recent readings (live stream proof) ───────
@router.get("/latest-readings", summary="📡 View last 20 readings (normal + spikes)")
def latest_readings() -> dict:
    """
    **Use this in Swagger UI to verify the simulator is running.**

    Returns the last 20 readings posted by the simulator,
    including both NORMAL and SPIKE_DETECTED readings with timestamps.
    Hit this endpoint every few seconds to see new data appear!
    """
    readings = get_recent_readings()
    return {
        "total": len(readings),
        "readings": readings
    }


# ── Queue a controlled spike (DEMO CONTROL) ───────────
@router.post("/queue-spike", summary="🎬 Queue a controlled spike for the live demo")
def queue_demo_spike(sensor_id: str) -> dict:
    """
    **DEMO CONTROL ENDPOINT.**

    Queues a spike for the specified sensor. The next reading the
    simulator generates for this sensor will GUARANTEE a spike above
    the threshold, triggering a real alert.

    Use this during your live demo to show a controlled spike!
    The spike is consumed after one use (one-shot).
    """
    sensor = sensor_manager.get_sensor(sensor_id)
    if not sensor:
        raise HTTPException(
            status_code=404,
            detail=f"Sensor '{sensor_id}' not found."
        )
    queue_spike(sensor_id)
    return {
        "status": "SPIKE_QUEUED",
        "sensor_id": sensor_id,
        "message": (
            f"Spike queued for sensor '{sensor_id}'. "
            f"The simulator will generate a spike on its next reading (within {5}s)."
        )
    }


# ── View current spike queue ──────────────────────────
@router.get("/queue-status", summary="View pending spike queue (admin)")
def queue_status() -> dict:
    """Returns sensors that have a spike queued and waiting to fire."""
    pending = get_queue_status()
    return {
        "pending_spikes": pending,
        "count": len(pending)
    }
