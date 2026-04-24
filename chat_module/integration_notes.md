# Integration Notes — Chat Module
## CrisisBridge AI — Cross-Module Contract

> **IMPORTANT:** This file is the contract between the isolated `chat_module/`
> and the rest of the CrisisBridge system. Nothing in this file has been
> implemented yet in the shared layer. This is a guide for **Person 3**
> to complete the connection when the team is ready.

---

## 1. What This Module Provides (Already Done)

The `chat_module` is a fully self-contained FastAPI app running on **port 8002**.
It has its own SQLite database (`chat_module/db/chat.db`) that is created automatically
on startup. It exposes the following stable API surface:

| Endpoint                              | Method    | Access  | Description                        |
|:--------------------------------------|:----------|:--------|:-----------------------------------|
| `/chat/start`                         | POST      | Guest   | Start a new chat session           |
| `/chat/sessions`                      | GET       | Admin   | List all sessions                  |
| `/chat/messages/{session_id}`         | GET       | Any     | Get message history                |
| `/chat/session/{session_id}/close`    | PATCH     | Admin   | Close a session                    |
| `/chat/session/{session_id}`          | DELETE    | Admin   | Permanently delete session + msgs  |
| `/chat/active`                        | GET       | Admin   | View live WebSocket connections    |
| `/ws/chat/{session_id}`               | WebSocket | Any     | Real-time chat connection          |

**WebSocket query params:**
```
ws://localhost:8002/ws/chat/{session_id}?sender_id=user_1&sender_role=guest
ws://localhost:8002/ws/chat/{session_id}?sender_id=staff_alice&sender_role=staff
```

---

## 2. Database Migration (SQLite → PostgreSQL)

Currently using SQLite for zero-setup portability. When moving to production:

### Step 1: Change one line in `config/settings.py`
```python
# FROM:
CHAT_DB_URL = f"sqlite:///{CHAT_DB_PATH}"

# TO:
CHAT_DB_URL = os.getenv(
    "CHAT_DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/crisisbridge"
)
```

### Step 2: Remove SQLite-specific arg in `db/repository.py`
```python
# FROM:
engine = create_engine(CHAT_DB_URL, connect_args={"check_same_thread": False})

# TO:
engine = create_engine(CHAT_DB_URL)
```

### Step 3: Add to `.env`
```env
CHAT_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/crisisbridge
```

**That's it — no other code changes needed.** SQLAlchemy handles the rest.

---

## 3. Authentication Integration (JWT)

Currently, `sender_id` is a plain text string passed as a query param.

### Future: Extract from JWT token

**In `api/routes.py`**, replace the query param approach:
```python
# ADD this import from shared layer:
from shared.dependencies import get_current_active_user
from shared.models import User

# MODIFY the WebSocket endpoint:
@ws_router.websocket("/chat/{session_id}")
async def websocket_chat(
    websocket: WebSocket,
    session_id: str,
    token: str,             # Client sends JWT as query param
):
    # Validate JWT manually (WebSockets can't use Depends for auth)
    user = verify_token(token)   # Implement using shared/dependencies logic
    await handle_chat_connection(
        websocket=websocket,
        session_id=session_id,
        sender_id=str(user.id),
        sender_role=user.role.value
    )
```

---

## 4. Shared Schema Changes Needed

When merging into the main app, add to `shared/schemas.py`:

```python
class ChatSessionResponse(BaseModel):
    session_id: str
    user_id: str
    status: str
    created_at: datetime

class ChatMessageResponse(BaseModel):
    message_id: str
    session_id: str
    sender_id: str
    sender_role: str
    message: str
    timestamp: datetime
```

---

## 5. Shared Model Changes Needed

When merging into `shared/models.py`, add:

```python
class ChatSession(Base):
    __tablename__ = "chat_sessions"
    session_id  = Column(String(36), primary_key=True)
    user_id     = Column(String(100), nullable=False)
    status      = Column(String(20), default="open")
    # FUTURE fields:
    priority_level  = Column(String(20), nullable=True)   # low/medium/high
    assigned_staff  = Column(String(100), nullable=True)  # staff_id
    created_at  = Column(DateTime, default=datetime.utcnow)

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    message_id  = Column(String(36), primary_key=True)
    session_id  = Column(String(36), ForeignKey("chat_sessions.session_id"))
    sender_id   = Column(String(100), nullable=False)
    sender_role = Column(String(20),  nullable=False)
    message     = Column(Text,        nullable=False)
    timestamp   = Column(DateTime,    default=datetime.utcnow)
```

---

## 6. Main App Router Registration

When Person 3 is ready to merge, add to the root `main.py`:

```python
from chat_module.api.routes import rest_router as chat_rest_router
from chat_module.api.routes import ws_router   as chat_ws_router

app.include_router(chat_rest_router, prefix="/api/v1")
app.include_router(chat_ws_router)
```

---

## 7. Admin Dashboard Integration

The admin panel should:
1. Call `GET /api/v1/chat/sessions` to list all open support chats
2. Call `GET /api/v1/chat/active` to see which sessions have live users
3. Connect via WebSocket using `sender_role=admin` to respond to guests
4. Call `PATCH /api/v1/chat/session/{id}/close` when done
5. Call `GET /api/v1/chat/active` on a polling interval to monitor load

---

## 8. How to Run (Current Isolated Mode)

```powershell
# Terminal 1 — Main app
uvicorn main:app --reload --port 8000

# Terminal 2 — Sensor module
uvicorn sensor_module.main:app --reload --port 8001

# Terminal 3 — Chat module
uvicorn chat_module.main:app --reload --port 8002
```

**Swagger UI:** `http://localhost:8002/docs`
**WebSocket test:** Use the Swagger UI or any WebSocket client (e.g., Postman, websocat)
