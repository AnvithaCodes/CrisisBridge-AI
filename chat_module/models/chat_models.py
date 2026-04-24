"""
Chat Database Models (SQLAlchemy — SQLite)
============================================
Defines the two tables for the chat system:
  - ChatSession : One per user conversation
  - ChatMessage : Every message in every session

Using SQLite for zero-setup local + cloud compatibility.
To migrate to PostgreSQL later, only the DB URL needs to change
(see integration_notes.md).
"""

import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, DateTime, create_engine
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


def _new_uuid() -> str:
    """Helper to generate a UUID string as primary key."""
    return str(uuid.uuid4())


class ChatSession(Base):
    """
    Represents a single support chat session.
    Created when a guest starts a new chat.
    """
    __tablename__ = "chat_sessions"

    session_id = Column(String(36), primary_key=True, default=_new_uuid)
    user_id    = Column(String(100), nullable=False)   # Guest who started the chat
    status     = Column(String(20),  default="open")   # open | closed
    created_at = Column(DateTime,    default=datetime.utcnow)


class ChatMessage(Base):
    """
    Represents a single message within a chat session.
    Every message (from guest or staff) is stored here.
    """
    __tablename__ = "chat_messages"

    message_id  = Column(String(36),  primary_key=True, default=_new_uuid)
    session_id  = Column(String(36),  nullable=False, index=True)
    sender_id   = Column(String(100), nullable=False)   # user_id or staff name
    sender_role = Column(String(20),  nullable=False)   # "guest" | "staff" | "admin"
    message     = Column(Text,        nullable=False)
    timestamp   = Column(DateTime,    default=datetime.utcnow)
