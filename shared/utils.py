"""
Shared Utility Functions for CrisisBridge AI
==============================================
Common helper functions used by multiple team members.

DO NOT put module-specific logic here.
Only add functions used by 2+ persons.
"""

import math
import uuid
import hashlib
import json
from datetime import datetime, timedelta
from typing import Optional
from shared.enums import (
    IncidentType, IncidentSeverity, IncidentPriority, SafetyLevel
)
from shared.config import settings


# ═══════════════════════════════════════════════════
#  DISTANCE & SAFETY CALCULATIONS
#  Used by: Person 1 (safety check), Person 3 (notifications)
# ═══════════════════════════════════════════════════

def calculate_distance_meters(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> float:
    """
    Calculate distance between two lat/lon points using Haversine formula.
    Returns distance in meters.
    """
    R = 6371000  # Earth's radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2) ** 2 +
         math.cos(phi1) * math.cos(phi2) *
         math.sin(delta_lambda / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def determine_safety_level(distance_meters: float) -> SafetyLevel:
    """
    Determine safety level based on distance from nearest active incident.
    Uses thresholds from config.
    """
    if distance_meters <= settings.SAFETY_RADIUS_EVACUATE_METERS:
        return SafetyLevel.EVACUATE
    elif distance_meters <= settings.SAFETY_RADIUS_WARNING_METERS:
        return SafetyLevel.WARNING
    else:
        return SafetyLevel.SAFE


def determine_safety_by_zone(
    user_floor: Optional[int],
    user_zone: Optional[str],
    incident_floor: Optional[int],
    incident_zone: Optional[str],
) -> SafetyLevel:
    """
    Zone-based safety check (when lat/lon not available).
    Same floor + same zone = EVACUATE
    Same floor, different zone = WARNING
    Different floor = SAFE (unless very close floors)
    """
    if user_floor is None or incident_floor is None:
        return SafetyLevel.WARNING  # Can't determine, be cautious

    floor_diff = abs(user_floor - incident_floor)

    if floor_diff == 0:
        if user_zone and incident_zone and user_zone == incident_zone:
            return SafetyLevel.EVACUATE
        return SafetyLevel.WARNING
    elif floor_diff <= 1:
        return SafetyLevel.WARNING
    else:
        return SafetyLevel.SAFE


# ═══════════════════════════════════════════════════
#  PRIORITY CALCULATION
#  Used by: Person 1 (incident creation)
# ═══════════════════════════════════════════════════

def calculate_priority(
    incident_type: IncidentType, severity: IncidentSeverity
) -> IncidentPriority:
    """
    Derive priority from incident type and severity.
    Fire/Critical = P1, Security/High = P2, etc.
    """
    # P1: Immediate
    if severity == IncidentSeverity.CRITICAL:
        return IncidentPriority.P1
    if incident_type == IncidentType.FIRE and severity in (
        IncidentSeverity.HIGH, IncidentSeverity.CRITICAL
    ):
        return IncidentPriority.P1

    # P2: Urgent
    if incident_type in (IncidentType.FIRE, IncidentType.SECURITY):
        return IncidentPriority.P2
    if incident_type == IncidentType.MEDICAL and severity == IncidentSeverity.HIGH:
        return IncidentPriority.P2

    # P3: High
    if severity == IncidentSeverity.HIGH:
        return IncidentPriority.P3
    if incident_type in (IncidentType.MEDICAL, IncidentType.INFRASTRUCTURE):
        return IncidentPriority.P3

    # P4: Normal
    return IncidentPriority.P4


# ═══════════════════════════════════════════════════
#  CACHING HELPERS
#  Used by: Person 3 (cache layer), Person 2 (query cache key)
# ═══════════════════════════════════════════════════

def generate_cache_key(query: str, session_id: Optional[str] = None) -> str:
    """
    Generate a deterministic cache key for a query.
    Normalizes the query (lowercase, strip) before hashing.
    """
    normalized = query.strip().lower()
    key_data = normalized
    if session_id:
        key_data = f"{session_id}:{normalized}"
    hash_val = hashlib.md5(key_data.encode()).hexdigest()
    return f"query_cache:{hash_val}"


def serialize_for_cache(data: dict) -> str:
    """Serialize a dict to JSON string for Redis storage."""
    return json.dumps(data, default=str)


def deserialize_from_cache(data: str) -> dict:
    """Deserialize a JSON string from Redis back to dict."""
    return json.loads(data)


# ═══════════════════════════════════════════════════
#  SESSION & ID HELPERS
#  Used by: Person 3 (session management), Person 2 (session tracking)
# ═══════════════════════════════════════════════════

def generate_session_id() -> str:
    """Generate a unique session ID."""
    return f"session_{uuid.uuid4().hex[:16]}"


def generate_request_id() -> str:
    """Generate a unique request ID for tracing."""
    return f"req_{uuid.uuid4().hex[:12]}"


# ═══════════════════════════════════════════════════
#  TIMESTAMP HELPERS
#  Used by: ALL
# ═══════════════════════════════════════════════════

def utc_now() -> datetime:
    """Get current UTC timestamp."""
    return datetime.utcnow()


def time_ago_str(dt: datetime) -> str:
    """Convert a datetime to a human-readable 'time ago' string."""
    diff = datetime.utcnow() - dt
    seconds = diff.total_seconds()

    if seconds < 60:
        return f"{int(seconds)}s ago"
    elif seconds < 3600:
        return f"{int(seconds // 60)}m ago"
    elif seconds < 86400:
        return f"{int(seconds // 3600)}h ago"
    else:
        return f"{int(seconds // 86400)}d ago"


def format_duration(start: datetime, end: datetime) -> str:
    """Format duration between two timestamps as human-readable string."""
    diff = end - start
    total_seconds = diff.total_seconds()

    if total_seconds < 60:
        return f"{total_seconds:.1f} seconds"
    elif total_seconds < 3600:
        return f"{total_seconds / 60:.1f} minutes"
    else:
        return f"{total_seconds / 3600:.1f} hours"


# ═══════════════════════════════════════════════════
#  JWT HELPERS
#  Used by: Person 3 (auth system)
#  Shared here because other modules may need to decode tokens
# ═══════════════════════════════════════════════════

def create_access_token(
    user_id: int,
    role: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a JWT access token.
    Payload: {"sub": user_id, "role": role, "exp": expiry}
    """
    from jose import jwt as jose_jwt

    to_encode = {
        "sub": str(user_id),
        "role": role,
    }
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode["exp"] = expire

    return jose_jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
