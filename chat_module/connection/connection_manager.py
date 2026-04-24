"""
WebSocket Connection Manager
==============================
Tracks all active WebSocket connections grouped by session_id.
Handles connect, disconnect, and broadcasting messages to all
participants in a session (guest + any staff who have joined).

This is the "traffic controller" of the real-time chat system.
It is completely stateless regarding the database — it only manages
live in-memory socket connections.
"""

from typing import Dict, List
from fastapi import WebSocket


class ConnectionManager:
    """
    Manages WebSocket connections per chat session.

    Structure:
        active_connections = {
            "session_id_1": [websocket_A, websocket_B],
            "session_id_2": [websocket_C],
            ...
        }

    Multiple staff members can join the same session, so each
    session maps to a LIST of active WebSocket connections.
    """

    def __init__(self):
        # session_id -> list of connected WebSockets
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, session_id: str, websocket: WebSocket):
        """
        Accept a new WebSocket connection and register it
        under the given session_id.
        """
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        self.active_connections[session_id].append(websocket)

    def disconnect(self, session_id: str, websocket: WebSocket):
        """
        Remove a WebSocket from a session's connection list.
        Cleans up the session key if no connections remain.
        """
        if session_id in self.active_connections:
            try:
                self.active_connections[session_id].remove(websocket)
            except ValueError:
                pass  # Already removed, safe to ignore
            # Clean up empty session slots
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]

    async def broadcast(self, session_id: str, message: dict):
        """
        Send a message (as JSON) to ALL participants in a session.
        This is how one sender's message reaches everyone else
        in the same chat session instantly.
        If a connection is broken, it is silently removed.
        """
        connections = self.active_connections.get(session_id, [])
        dead_connections = []

        for websocket in connections:
            try:
                await websocket.send_json(message)
            except Exception:
                # Connection is dead — mark for removal
                dead_connections.append(websocket)

        # Clean up any dead connections found during broadcast
        for ws in dead_connections:
            self.disconnect(session_id, ws)

    def get_active_count(self, session_id: str) -> int:
        """Returns the number of participants currently connected to a session."""
        return len(self.active_connections.get(session_id, []))

    def get_all_active_sessions(self) -> List[str]:
        """Returns all session IDs that currently have at least one live connection."""
        return list(self.active_connections.keys())


# ── Singleton Instance ────────────────────────────────
# One shared manager for the entire app lifetime.
# Imported and used by both ws_handler.py and routes.py.
manager = ConnectionManager()
