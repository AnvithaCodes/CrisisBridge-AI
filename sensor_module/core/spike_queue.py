"""
Spike Queue — Demo Control System
===================================
Allows external callers (API, frontend) to queue a forced spike
for a specific sensor. The simulator checks this queue before
each reading and generates a spike if one is requested.

This is what makes the live demo controllable!
"""

# In-memory queue: { sensor_id -> True if spike pending }
_spike_queue: dict[str, bool] = {}


def queue_spike(sensor_id: str):
    """Request a spike for the given sensor on its next reading."""
    _spike_queue[sensor_id] = True


def consume_spike(sensor_id: str) -> bool:
    """
    Check if a spike is queued for this sensor.
    Consumes it (one-shot) and returns True if a spike was pending.
    """
    if _spike_queue.get(sensor_id):
        _spike_queue[sensor_id] = False
        return True
    return False


def get_queue_status() -> dict:
    """Returns the current state of the spike queue (for admin visibility)."""
    return {sid: pending for sid, pending in _spike_queue.items() if pending}
