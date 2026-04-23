"""
Shared ORM Models for CrisisBridge AI
=======================================
Contains database table definitions used by MULTIPLE team members.

Rules:
- If a table is used by only ONE person, define it in their module instead.
- All models here MUST inherit from shared.database.Base
- After adding a model, run init_db() to create the table.

Tables defined here:
- User          → Used by ALL (auth, incidents, feedback, AI sessions)
- Incident      → Used by Person 1 (creator) + Person 3 (logs/dashboard) + Frontend (all)
- QueryLog      → Used by Person 2 (AI) + Person 3 (caching/logging)
- Feedback      → Used by Person 3 (creator) + all frontends
- Notification  → Used by Person 1 (incident alerts) + Person 3 (delivery)
- SessionMemory → Used by Person 2 (AI context) + Person 3 (Redis sync)
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean,
    DateTime, ForeignKey, Enum as SAEnum, JSON
)
from sqlalchemy.orm import relationship
from shared.database import Base
from shared.enums import (
    UserRole, IncidentType, IncidentSeverity, IncidentStatus,
    IncidentPriority, FeedbackRating, FeedbackTargetType,
    NotificationType, CacheStatus, SafetyLevel
)


# ═══════════════════════════════════════════════════
# USER TABLE
# Created by: Person 3 (Backend/Auth)
# Used by: ALL
# ═══════════════════════════════════════════════════

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(200), nullable=True)
    role = Column(SAEnum(UserRole), nullable=False, default=UserRole.GUEST)
    
    # Location info (for safety checks)
    current_floor = Column(Integer, nullable=True)
    current_room = Column(String(50), nullable=True)
    current_zone = Column(String(50), nullable=True)  # e.g., "lobby", "pool", "restaurant"
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    reported_incidents = relationship("Incident", back_populates="reporter", foreign_keys="Incident.reporter_id")
    assigned_incidents = relationship("Incident", back_populates="assigned_staff", foreign_keys="Incident.assigned_staff_id")
    feedbacks = relationship("Feedback", back_populates="user")
    notifications = relationship("Notification", back_populates="user")


# ═══════════════════════════════════════════════════
# INCIDENT TABLE
# Created by: Person 1 (Incident System)
# Used by: Person 1 (CRUD), Person 3 (logs/dashboard), Frontend (all)
# ═══════════════════════════════════════════════════

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Core info
    incident_type = Column(SAEnum(IncidentType), nullable=False)
    severity = Column(SAEnum(IncidentSeverity), nullable=False, default=IncidentSeverity.MEDIUM)
    priority = Column(SAEnum(IncidentPriority), nullable=False, default=IncidentPriority.P3)
    status = Column(SAEnum(IncidentStatus), nullable=False, default=IncidentStatus.REPORTED)
    
    # Description
    title = Column(String(300), nullable=False)
    description = Column(Text, nullable=True)
    
    # Location
    floor = Column(Integer, nullable=True)
    room = Column(String(50), nullable=True)
    zone = Column(String(100), nullable=True)  # "lobby", "kitchen", "pool_area"
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # People
    reporter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_staff_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Timeline
    reported_at = Column(DateTime, default=datetime.utcnow)
    acknowledged_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    closed_at = Column(DateTime, nullable=True)
    
    # Resolution
    resolution_notes = Column(Text, nullable=True)

    # Relationships
    reporter = relationship("User", back_populates="reported_incidents", foreign_keys=[reporter_id])
    assigned_staff = relationship("User", back_populates="assigned_incidents", foreign_keys=[assigned_staff_id])
    feedbacks = relationship("Feedback", back_populates="incident")


# ═══════════════════════════════════════════════════
# QUERY LOG TABLE
# Created by: Person 3 (Logging)
# Used by: Person 2 (AI writes results), Person 3 (caching/analytics)
# ═══════════════════════════════════════════════════

class QueryLog(Base):
    __tablename__ = "query_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Query info
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Nullable for anonymous
    session_id = Column(String(100), nullable=True, index=True)
    original_query = Column(Text, nullable=False)
    rewritten_query = Column(Text, nullable=True)  # After query rewriting agent
    
    # Response info
    answer = Column(Text, nullable=True)
    sources = Column(JSON, nullable=True)  # List of source references
    confidence = Column(Float, nullable=True)
    explanation = Column(Text, nullable=True)
    
    # Performance
    cache_status = Column(SAEnum(CacheStatus), nullable=True)
    response_time_ms = Column(Float, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)


# ═══════════════════════════════════════════════════
# FEEDBACK TABLE
# Created by: Person 3 (Feedback System)
# Used by: All frontends
# ═══════════════════════════════════════════════════

class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    target_type = Column(SAEnum(FeedbackTargetType), nullable=False)
    
    # Reference to what's being rated
    query_log_id = Column(Integer, ForeignKey("query_logs.id"), nullable=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=True)
    
    # Feedback content
    rating = Column(SAEnum(FeedbackRating), nullable=False)
    comment = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="feedbacks")
    incident = relationship("Incident", back_populates="feedbacks")


# ═══════════════════════════════════════════════════
# NOTIFICATION TABLE
# Created by: Person 3 (Notification delivery)
# Populated by: Person 1 (incident alerts), Person 3 (broadcast)
# Used by: All frontends
# ═══════════════════════════════════════════════════

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    notification_type = Column(SAEnum(NotificationType), nullable=False)
    
    title = Column(String(300), nullable=False)
    message = Column(Text, nullable=False)
    
    # Reference (optional link to incident)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=True)
    
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="notifications")
