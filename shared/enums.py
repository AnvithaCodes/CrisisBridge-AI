"""
Shared Enumerations for CrisisBridge AI
========================================
Used by ALL team members. DO NOT modify without team agreement.

Contains all enum types used across:
- Incident system (Person 1)
- AI Core (Person 2)
- Backend/Infra (Person 3)
"""

from enum import Enum


# ─────────────────────────────────────────────
# User & Auth Enums
# ─────────────────────────────────────────────

class UserRole(str, Enum):
    """User roles in the system."""
    GUEST = "guest"
    STAFF = "staff"
    ADMIN = "admin"


# ─────────────────────────────────────────────
# Incident Enums
# ─────────────────────────────────────────────

class IncidentType(str, Enum):
    """Types of emergency incidents."""
    FIRE = "fire"
    MEDICAL = "medical"
    SECURITY = "security"
    INFRASTRUCTURE = "infrastructure"  # power outage, elevator stuck, gas leak, water leak
    NATURAL_DISASTER = "natural_disaster"  # flood, earthquake, storm
    OTHER = "other"


class IncidentSeverity(str, Enum):
    """Severity levels for incidents."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentStatus(str, Enum):
    """Status of an incident through its lifecycle."""
    REPORTED = "reported"
    ACKNOWLEDGED = "acknowledged"
    RESPONDING = "responding"
    RESOLVED = "resolved"
    CLOSED = "closed"


class IncidentPriority(str, Enum):
    """Priority classification derived from type + severity."""
    P1 = "p1"  # Immediate (fire, critical medical)
    P2 = "p2"  # Urgent (security threat, gas leak)
    P3 = "p3"  # High (medical non-critical, infrastructure)
    P4 = "p4"  # Normal (minor issues)


# ─────────────────────────────────────────────
# Safety Enums
# ─────────────────────────────────────────────

class SafetyLevel(str, Enum):
    """Safety assessment result."""
    SAFE = "safe"
    WARNING = "warning"
    EVACUATE = "evacuate"


# ─────────────────────────────────────────────
# AI / Query Enums
# ─────────────────────────────────────────────

class QueryCategory(str, Enum):
    """Categories for user queries to the AI assistant."""
    EMERGENCY_GUIDANCE = "emergency_guidance"
    EVACUATION = "evacuation"
    FIRST_AID = "first_aid"
    SAFETY_PROTOCOL = "safety_protocol"
    GENERAL = "general"


class CacheStatus(str, Enum):
    """Whether a response was served from cache."""
    HIT = "hit"
    MISS = "miss"


# ─────────────────────────────────────────────
# Feedback Enums
# ─────────────────────────────────────────────

class FeedbackRating(str, Enum):
    """User feedback on AI responses or system actions."""
    HELPFUL = "helpful"
    NOT_HELPFUL = "not_helpful"


class FeedbackTargetType(str, Enum):
    """What the feedback is about."""
    AI_RESPONSE = "ai_response"
    INCIDENT_RESPONSE = "incident_response"
    SYSTEM = "system"


# ─────────────────────────────────────────────
# Notification Enums
# ─────────────────────────────────────────────

class NotificationType(str, Enum):
    """Types of notifications sent to users."""
    INCIDENT_ALERT = "incident_alert"
    STATUS_UPDATE = "status_update"
    SAFETY_ALERT = "safety_alert"
    BROADCAST = "broadcast"
    ASSIGNMENT = "assignment"
