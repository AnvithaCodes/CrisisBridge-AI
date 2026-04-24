"""
Sensor Manager — In-Memory Store
==================================
Manages registered sensors. Completely isolated, no external dependencies.
"""
from typing import Dict, List, Optional
from sensor_module.models.sensor_model import Sensor

# In-memory store: { sensor_id -> Sensor }
_sensors: Dict[str, Sensor] = {}

def register_sensor(sensor: Sensor) -> Sensor:
    """Register a new sensor. Overwrites if sensor_id already exists."""
    _sensors[sensor.sensor_id] = sensor
    return sensor

def get_sensor(sensor_id: str) -> Optional[Sensor]:
    """Get a sensor by its ID. Returns None if not found."""
    return _sensors.get(sensor_id)

def list_sensors() -> List[Sensor]:
    """Return all registered sensors."""
    return list(_sensors.values())

def remove_sensor(sensor_id: str) -> bool:
    """Remove a sensor. Returns True if it existed."""
    if sensor_id in _sensors:
        del _sensors[sensor_id]
        return True
    return False

def seed_demo_sensors():
    """
    Pre-loads 3 demo sensors for the hackathon demo so the system
    is not empty when first launched.
    """
    demo_sensors = [
        Sensor(sensor_id="S1", type="smoke",    zone="floor_2_corridor",  threshold=70.0),
        Sensor(sensor_id="S2", type="fire",     zone="floor_3_kitchen",   threshold=80.0),
        Sensor(sensor_id="S3", type="gas",      zone="basement_boiler",   threshold=60.0),
    ]
    for s in demo_sensors:
        _sensors[s.sensor_id] = s
