"""
Chat Service — Business Logic Layer
=====================================
Sits between the API/WebSocket layer and the database repository.
Coordinates message saving, session validation, and history retrieval.
Keeps the route handlers thin and clean.
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from chat_module.db import repository
from chat_module.schemas.chat_schema import (
    StartChatResponse,
    MessageResponse,
    ChatHistoryResponse,
    SessionListResponse,
    WebSocketMessage,
)


def start_session(db: Session, user_id: str) -> StartChatResponse:
    """
    Creates a new chat session for a guest.
    Each call produces a unique session_id the client uses
    to connect via WebSocket.
    """
    session = repository.create_session(db, user_id=user_id)
    return StartChatResponse.from_orm(session)


def get_history(db: Session, session_id: str) -> ChatHistoryResponse:
    """
    Returns full message history for a session.
    Raises 404 if the session does not exist.
    """
    session = repository.get_session(db, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chat session '{session_id}' not found."
        )

    messages = repository.get_messages(db, session_id)
    return ChatHistoryResponse(
        session_id=session_id,
        messages=[MessageResponse.from_orm(m) for m in messages],
        total=len(messages)
    )


def list_all_sessions(db: Session) -> SessionListResponse:
    """
    Returns all sessions (for admin dashboard use).
    """
    sessions = repository.list_sessions(db)
    return SessionListResponse(
        sessions=[StartChatResponse.from_orm(s) for s in sessions],
        total=len(sessions)
    )


def close_session(db: Session, session_id: str) -> dict:
    """
    Marks a session as closed (staff/admin action).
    Raises 404 if session not found.
    """
    session = repository.close_session(db, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chat session '{session_id}' not found."
        )
    return {"status": "closed", "session_id": session_id}


def process_and_save_message(
    db: Session,
    session_id: str,
    ws_message: WebSocketMessage
) -> dict:
    """
    Validates the session, persists the message to the database,
    and returns a broadcast-ready dict (with timestamp).

    Called from the WebSocket handler on every incoming message.
    """
    # Validate session exists
    session = repository.get_session(db, session_id)
    if not session:
        raise ValueError(f"Session '{session_id}' does not exist.")

    if session.status == "closed":
        raise ValueError(f"Session '{session_id}' is already closed.")

    # Persist to DB
    saved = repository.save_message(
        db=db,
        session_id=session_id,
        sender_id=ws_message.sender_id,
        sender_role=ws_message.sender_role,
        message=ws_message.message
    )

    # Return broadcast-ready dict
    return {
        "message_id":  saved.message_id,
        "session_id":  session_id,
        "sender_id":   saved.sender_id,
        "sender_role": saved.sender_role,
        "message":     saved.message,
        "timestamp":   saved.timestamp.isoformat()
    }
