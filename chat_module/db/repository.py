"""
Chat Database Repository
=========================
All database operations for the chat module.
Uses SQLite via SQLAlchemy — zero setup required locally or on Google Cloud.

Handles:
  - DB engine creation and table initialization
  - Session CRUD
  - Message insert and retrieval
"""

import os
from typing import List, Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from chat_module.models.chat_models import Base, ChatSession, ChatMessage
from chat_module.config.settings import CHAT_DB_URL, MAX_HISTORY_MESSAGES

# ── Engine Setup ──────────────────────────────────────
# check_same_thread=False is required for SQLite with FastAPI async context
engine = create_engine(
    CHAT_DB_URL,
    connect_args={"check_same_thread": False},
    echo=False   # Set to True to debug SQL queries
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """
    Creates all tables if they don't already exist.
    Safe to call on every startup — it won't overwrite existing data.
    """
    # Ensure the directory for the SQLite file exists
    db_dir = os.path.dirname(CHAT_DB_URL.replace("sqlite:///", ""))
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    Base.metadata.create_all(bind=engine)


def get_db() -> Session:
    """Dependency-style DB session factory."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── Session Operations ────────────────────────────────

def create_session(db: Session, user_id: str) -> ChatSession:
    """Create and persist a new chat session for a guest user."""
    session = ChatSession(user_id=user_id)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_session(db: Session, session_id: str) -> Optional[ChatSession]:
    """Fetch a single chat session by ID."""
    return db.query(ChatSession).filter(
        ChatSession.session_id == session_id
    ).first()


def list_sessions(db: Session) -> List[ChatSession]:
    """Return all chat sessions (admin use)."""
    return db.query(ChatSession).order_by(
        ChatSession.created_at.desc()
    ).all()


def close_session(db: Session, session_id: str) -> Optional[ChatSession]:
    """Mark a session as closed."""
    session = get_session(db, session_id)
    if session:
        session.status = "closed"
        db.commit()
        db.refresh(session)
    return session


# ── Message Operations ────────────────────────────────

def save_message(
    db: Session,
    session_id: str,
    sender_id: str,
    sender_role: str,
    message: str
) -> ChatMessage:
    """Persist a new chat message to the database."""
    msg = ChatMessage(
        session_id=session_id,
        sender_id=sender_id,
        sender_role=sender_role,
        message=message
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


def get_messages(
    db: Session,
    session_id: str,
    limit: int = MAX_HISTORY_MESSAGES
) -> List[ChatMessage]:
    """
    Retrieve message history for a session.
    Returns the most recent `limit` messages, ordered oldest-first
    so clients can render them in the correct order.
    """
    return (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.timestamp.asc())
        .limit(limit)
        .all()
    )
