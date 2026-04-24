"""
WebSocket Handler
==================
The real-time engine of the chat module.

Flow per connection:
  1. Client connects to /ws/chat/{session_id}?sender_id=X&sender_role=Y
  2. Connection accepted and registered in ConnectionManager
  3. Last 20 messages are replayed to the new participant
  4. Loop: receive message → save to DB → broadcast to all in session
  5. On disconnect: cleanly remove from ConnectionManager

Designed to handle both guests and multiple staff members
joining the same session simultaneously.
"""

from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from chat_module.connection.connection_manager import manager
from chat_module.service import chat_service
from chat_module.schemas.chat_schema import WebSocketMessage
from chat_module.db.repository import get_messages, get_session, SessionLocal


async def handle_chat_connection(
    websocket: WebSocket,
    session_id: str,
    sender_id: str,
    sender_role: str
):
    """
    Main WebSocket lifecycle handler.
    Called once per client connection from the router.

    Args:
        websocket   : The FastAPI WebSocket object
        session_id  : The session this client is joining
        sender_id   : Identity of the connecting user (guest ID or staff name)
        sender_role : "guest" | "staff" | "admin"
    """
    db = SessionLocal()
    try:
        # 0. Validate Session and Guest Identity before accepting
        session = get_session(db, session_id)
        if not session:
            await websocket.close(code=4004, reason="Session not found")
            return
            
        if sender_role == "guest" and sender_id != session.user_id:
            # Only the original creator can join as the guest.
            # Other guests trying to snoop on this session are rejected.
            await websocket.close(code=4003, reason="Unauthorized: Only the original guest can join this session.")
            return

        # 1. Accept & register the connection
        await manager.connect(session_id, websocket)

        # Notify all participants that someone joined
        join_event = {
            "event":       "user_joined",
            "sender_id":   sender_id,
            "sender_role": sender_role,
            "message":     f"{sender_role.capitalize()} '{sender_id}' has joined the chat.",
            "session_id":  session_id,
            "active_users": manager.get_active_count(session_id)
        }
        await manager.broadcast(session_id, join_event)

        # 2. Replay recent message history to the newly connected participant
        history = get_messages(db, session_id, limit=20)
        if history:
            await websocket.send_json({
                "event": "history",
                "messages": [
                    {
                        "message_id":  m.message_id,
                        "sender_id":   m.sender_id,
                        "sender_role": m.sender_role,
                        "message":     m.message,
                        "timestamp":   m.timestamp.isoformat()
                    }
                    for m in history
                ]
            })
    finally:
        db.close()

    # 3. Main message loop
    try:
        while True:
            # Wait for a message from this client
            raw = await websocket.receive_json()

            # Parse and validate the incoming message
            try:
                ws_msg = WebSocketMessage(
                    sender_id=raw.get("sender_id", sender_id),
                    sender_role=raw.get("sender_role", sender_role),
                    message=raw.get("message", "")
                )
            except Exception:
                await websocket.send_json({
                    "event": "error",
                    "message": "Invalid message format. Expected: {sender_id, sender_role, message}"
                })
                continue

            # Skip empty messages
            if not ws_msg.message.strip():
                continue

            # Save to DB and get broadcast-ready payload
            db = SessionLocal()
            try:
                payload = chat_service.process_and_save_message(
                    db=db,
                    session_id=session_id,
                    ws_message=ws_msg
                )
                payload["event"] = "message"
            except ValueError as e:
                await websocket.send_json({"event": "error", "message": str(e)})
                db.close()
                break
            finally:
                db.close()

            # Broadcast to ALL participants in this session (including sender)
            await manager.broadcast(session_id, payload)

    except WebSocketDisconnect:
        # 4. Clean disconnect
        manager.disconnect(session_id, websocket)

        # Notify remaining participants
        leave_event = {
            "event":       "user_left",
            "sender_id":   sender_id,
            "sender_role": sender_role,
            "message":     f"{sender_role.capitalize()} '{sender_id}' has left the chat.",
            "session_id":  session_id,
            "active_users": manager.get_active_count(session_id)
        }
        await manager.broadcast(session_id, leave_event)

    except Exception as e:
        # Unexpected errors — disconnect cleanly and log
        manager.disconnect(session_id, websocket)
        print(f"[Chat WS Error] session={session_id} sender={sender_id}: {e}")
