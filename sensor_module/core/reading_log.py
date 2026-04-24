"""
Reading Log — Stores recent normal + spike readings for visibility
===================================================================
Allows the Swagger UI to show proof that the simulator is actively
streaming data, even for normal (non-spike) readings.
"""
from sensor_module.models.sensor_model import SensorReading

_recent_readings: list[dict] = []
MAX_READINGS = 20  # Keep only the last 20 readings in memory


def log_reading(reading: SensorReading, status: str):
    """Log a reading with its status (NORMAL or SPIKE_DETECTED)."""
    entry = {
        "sensor_id": reading.sensor_id,
        "value": reading.value,
        "status": status,
        "timestamp": reading.timestamp.isoformat()
    }
    _recent_readings.append(entry)
    if len(_recent_readings) > MAX_READINGS:
        _recent_readings.pop(0)


def get_recent_readings() -> list[dict]:
    """Return the last 20 readings (most recent first)."""
    return list(reversed(_recent_readings))
