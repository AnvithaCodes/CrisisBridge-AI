"""
Chat Module Settings
=====================
All configuration for the isolated chat module.
Uses SQLite stored inside this module's folder — zero external setup required.
Works identically on local machines and Google Cloud.
"""

import os

# ── Database ──────────────────────────────────────────
# SQLite file stored inside the module directory itself.
# Path is relative to where the server is started from (project root).
CHAT_DB_PATH = os.getenv("CHAT_DB_PATH", "chat_module/db/chat.db")
CHAT_DB_URL  = f"sqlite:///{CHAT_DB_PATH}"

# ── Server ────────────────────────────────────────────
CHAT_PORT        = int(os.getenv("CHAT_PORT", 8002))
CHAT_HOST        = os.getenv("CHAT_HOST", "0.0.0.0")

# ── Message History ───────────────────────────────────
# Max messages returned per history request (prevents huge payloads)
MAX_HISTORY_MESSAGES = int(os.getenv("MAX_HISTORY_MESSAGES", 100))
