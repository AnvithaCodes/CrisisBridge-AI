"""
Chat Pydantic Schemas
======================
Defines the request/response shapes for the Chat REST API.
These are completely isolated from shared/schemas.py.
When integrating with the main app later, these can either be
merged into shared/schemas.py or kept separate (see integration_notes.md).
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# ── Requests ──────────────────────────────────────────

class StartChatRequest(BaseModel):
    """Body for POST /chat/start"""
    user_id: str                      # Guest's identifier (e.g., "user_123")
    sender_role: Optional[str] = "guest"  # Default role is guest


class JoinChatRequest(BaseModel):
    """Body for POST /chat/join — staff joining an existing session"""
    session_id: str
    staff_id: str
    sender_role: Optional[str] = "staff"


# ── Responses ─────────────────────────────────────────

class StartChatResponse(BaseModel):
    """Response for POST /chat/start"""
    session_id: str
    user_id: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    """Single message shape — used in history and WebSocket broadcasts"""
    message_id: str
    session_id: str
    sender_id: str
    sender_role: str
    message: str
    timestamp: datetime

    class Config:
        from_attributes = True


class ChatHistoryResponse(BaseModel):
    """Response for GET /chat/messages/{session_id}"""
    session_id: str
    messages: List[MessageResponse]
    total: int


class SessionListResponse(BaseModel):
    """Response for GET /chat/sessions — admin view of all sessions"""
    sessions: List[StartChatResponse]
    total: int


# ── WebSocket Message Format ───────────────────────────

class WebSocketMessage(BaseModel):
    """
    The shape of every message sent over the WebSocket connection.
    Clients must send JSON in this format.
    """
    sender_id:   str
    sender_role: str                  # "guest" | "staff" | "admin"
    message:     str
