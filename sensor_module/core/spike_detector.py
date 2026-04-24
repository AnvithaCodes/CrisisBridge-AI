"""
Spike Detector — Anomaly Detection Logic
==========================================
Compares incoming sensor readings against thresholds.
Returns structured SensorAlert objects on spikes. Fully stateless.
"""
from datetime import datetime
from typing import Optional
from sensor_module.models.sensor_model import Sensor, SensorAlert

# In-memory log of recent alerts (kept in memory, no DB required)
_recent_alerts: list[SensorAlert] = []
MAX_ALERT_HISTORY = 100  # Only keep the last 100 alerts in memory

def detect_spike(sensor: Sensor, value: float) -> Optional[SensorAlert]:
    """
    Core detection logic.
    Returns a SensorAlert if the value exceeds the sensor's threshold,
    otherwise returns None.
    """
    if value > sensor.threshold:
        alert = SensorAlert(
            sensor_id=sensor.sensor_id,
            type=sensor.type,
            zone=sensor.zone,
            value=value,
            threshold=sensor.threshold,
            message=(
                f"⚠️ SPIKE DETECTED on sensor '{sensor.sensor_id}'! "
                f"Type: {sensor.type.upper()} | Zone: {sensor.zone} | "
                f"Value: {value} > Threshold: {sensor.threshold}"
            ),
            timestamp=datetime.utcnow()
        )
        _log_alert(alert)
        return alert
    return None

def _log_alert(alert: SensorAlert):
    """Append alert to in-memory log with a cap to prevent memory leaks."""
    _recent_alerts.append(alert)
    if len(_recent_alerts) > MAX_ALERT_HISTORY:
        _recent_alerts.pop(0)  # Remove oldest

def get_recent_alerts() -> list[SensorAlert]:
    """Return the in-memory log of recent alerts (most recent last)."""
    return list(reversed(_recent_alerts))

def clear_alerts():
    """Clear all recent alerts from memory."""
    _recent_alerts.clear()
