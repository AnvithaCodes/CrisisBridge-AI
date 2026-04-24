"""
Chat Module — Standalone FastAPI Application
==============================================
Runs COMPLETELY ISOLATED on port 8002.

Ports used by the full CrisisBridge system:
  8000 — Main app
  8001 — Sensor module
  8002 — Chat module  ← This file

How to run:
    uvicorn chat_module.main:app --reload --port 8002

Swagger UI (REST endpoints only):
    http://localhost:8002/docs

WebSocket Test (use Swagger or a WS client):
    ws://localhost:8002/ws/chat/{session_id}?sender_id=user_1&sender_role=guest
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from chat_module.api.routes import rest_router, ws_router
from chat_module.db.repository import init_db

# ── Create App ───────────────────────────────────────
app = FastAPI(
    title="CrisisBridge — Live Chat Module",
    version="1.0.0",
    description=(
        "Real-time WebSocket-based support chat system. "
        "Isolated module running on port 8002. "
        "Supports multiple staff responders per session."
    ),
)

# ── CORS ─────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # Tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register Routers ─────────────────────────────────
app.include_router(rest_router)
app.include_router(ws_router)


# ── Startup ──────────────────────────────────────────
@app.on_event("startup")
def on_startup():
    """Initialize the SQLite database tables on startup."""
    init_db()
    print("✅ Chat Module started — SQLite database initialized.")
    print("📡 REST API:   http://localhost:8002/docs")
    print("🔌 WebSocket:  ws://localhost:8002/ws/chat/{session_id}")


# ── Health Check ─────────────────────────────────────
@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "module": "chat_module", "port": 8002}
