# 📡 CrisisBridge AI — API Registry & Contract

> **This is the single source of truth for ALL APIs.**  
> Every endpoint, who builds it, who uses it, and the exact request/response schemas.

---

## 🔑 Legend

| Symbol | Meaning |
|--------|---------|
| 🔓 | Public (no auth required) |
| 🔒 | Auth required (any role) |
| 👤 | Guest only |
| 👷 | Staff only |
| 👑 | Admin only |
| 👷👑 | Staff + Admin |

---

## 📋 Complete API Table

| # | Method | Endpoint | Owner | Used By | Auth | Description |
|---|--------|----------|-------|---------|------|-------------|
| 1 | `GET` | `/api/v1/health` | Person 3 | ALL | 🔓 | System health check |
| 2 | `POST` | `/api/v1/auth/register` | Person 3 | ALL | 🔓 | Register new user |
| 3 | `POST` | `/api/v1/auth/login` | Person 3 | ALL | 🔓 | Login, get JWT token |
| 4 | `GET` | `/api/v1/auth/me` | Person 3 | ALL | 🔒 | Get current user profile |
| 5 | `PATCH` | `/api/v1/users/me/location` | Person 3 | ALL | 🔒 | Update user location |
| 6 | `POST` | `/api/v1/incidents/report` | **Person 1** | ALL | 🔒 | Report incident (panic button) |
| 7 | `GET` | `/api/v1/incidents` | **Person 1** | ALL | 🔒 | List all incidents (filterable) |
| 8 | `GET` | `/api/v1/incidents/{id}` | **Person 1** | ALL | 🔒 | Get single incident details |
| 9 | `PATCH` | `/api/v1/incidents/{id}/status` | **Person 1** | Staff/Admin | 👷👑 | Update incident status/assignment |
| 10 | `GET` | `/api/v1/incidents/stats` | **Person 1** | ALL | 🔒 | Dashboard statistics |
| 11 | `POST` | `/api/v1/safety/check` | **Person 1** | ALL | 🔒 | Check safety at location |
| 12 | `POST` | `/api/v1/query` | Person 3 (route) + **Person 2** (processing) | ALL | 🔒 | AI crisis assistant query |
| 13 | `POST` | `/api/v1/feedback` | Person 3 | ALL | 🔒 | Submit feedback on AI/system |
| 14 | `GET` | `/api/v1/feedback/stats` | Person 3 | Admin | 👑 | Feedback analytics |
| 15 | `GET` | `/api/v1/notifications` | Person 3 | ALL | 🔒 | Get user's notifications |
| 16 | `PATCH` | `/api/v1/notifications/{id}/read` | Person 3 | ALL | 🔒 | Mark notification as read |
| 17 | `POST` | `/api/v1/notifications/broadcast` | Person 3 | Admin | 👑 | Broadcast message to all |

---

## 📝 Detailed API Specifications

---

### 1. `GET /api/v1/health` 🔓
**Owner:** Person 3 | **Used by:** ALL

```
Response: HealthResponse
{
  "status": "ok",
  "version": "1.0.0",
  "database": "connected",
  "redis": "connected",
  "faiss": "loaded"
}
```

---

### 2. `POST /api/v1/auth/register` 🔓
**Owner:** Person 3 | **Used by:** ALL

```
Request: UserRegister
{
  "email": "guest@hotel.com",
  "username": "john_doe",
  "password": "securepass123",
  "full_name": "John Doe",
  "role": "guest"
}

Response: TokenResponse
{
  "access_token": "eyJhbGciOiJI...",
  "token_type": "bearer",
  "user": { ...UserResponse }
}
```

---

### 3. `POST /api/v1/auth/login` 🔓
**Owner:** Person 3 | **Used by:** ALL

```
Request: UserLogin
{
  "email": "guest@hotel.com",
  "password": "securepass123"
}

Response: TokenResponse (same as register)
```

---

### 4. `GET /api/v1/auth/me` 🔒
**Owner:** Person 3 | **Used by:** ALL

```
Headers: Authorization: Bearer <token>

Response: UserResponse
{
  "id": 1,
  "email": "guest@hotel.com",
  "username": "john_doe",
  "full_name": "John Doe",
  "role": "guest",
  "current_floor": 3,
  "current_room": "305",
  "current_zone": "east_wing",
  "is_active": true,
  "created_at": "2026-04-23T10:00:00"
}
```

---

### 5. `PATCH /api/v1/users/me/location` 🔒
**Owner:** Person 3 | **Used by:** ALL

```
Request: UserLocationUpdate
{
  "current_floor": 3,
  "current_room": "305",
  "current_zone": "east_wing"
}

Response: UserResponse
```

---

### 6. `POST /api/v1/incidents/report` 🔒
**Owner:** Person 1 | **Used by:** ALL (Panic Button)

```
Request: IncidentCreate
{
  "incident_type": "fire",
  "severity": "high",
  "title": "Fire in Room 305",
  "description": "Smoke visible from under the door",
  "floor": 3,
  "room": "305",
  "zone": "east_wing"
}

Response: IncidentResponse
{
  "id": 1,
  "incident_type": "fire",
  "severity": "high",
  "priority": "p1",
  "status": "reported",
  "title": "Fire in Room 305",
  ...
  "reported_at": "2026-04-23T10:05:00"
}
```

---

### 7. `GET /api/v1/incidents` 🔒
**Owner:** Person 1 | **Used by:** ALL (Dashboard)

```
Query Params: ?status=reported&type=fire&page=1&page_size=20

Response: IncidentListResponse
{
  "incidents": [ ...IncidentResponse ],
  "total": 15,
  "active_count": 3
}
```

---

### 8. `GET /api/v1/incidents/{id}` 🔒
**Owner:** Person 1 | **Used by:** ALL

```
Response: IncidentResponse
```

---

### 9. `PATCH /api/v1/incidents/{id}/status` 👷👑
**Owner:** Person 1 | **Used by:** Staff/Admin

```
Request: IncidentUpdate
{
  "status": "responding",
  "assigned_staff_id": 5,
  "resolution_notes": "Fire team dispatched"
}

Response: IncidentResponse
```

---

### 10. `GET /api/v1/incidents/stats` 🔒
**Owner:** Person 1 | **Used by:** ALL (Dashboard)

```
Response: IncidentStats
{
  "total_incidents": 47,
  "active_incidents": 3,
  "resolved_today": 5,
  "avg_resolution_time_minutes": 12.5,
  "by_type": {"fire": 10, "medical": 20, "security": 17},
  "by_status": {"reported": 2, "responding": 1, "resolved": 44},
  "by_severity": {"low": 15, "medium": 20, "high": 10, "critical": 2}
}
```

---

### 11. `POST /api/v1/safety/check` 🔒
**Owner:** Person 1 | **Used by:** ALL (Safety Button)

```
Request: SafetyCheckRequest
{
  "floor": 3,
  "room": "305",
  "zone": "east_wing"
}

Response: SafetyCheckResponse
{
  "safety_level": "warning",
  "message": "An incident is reported on your floor",
  "nearby_incidents": [ ...IncidentResponse ],
  "recommended_action": "Move to nearest exit on Floor 3 - West Wing",
  "nearest_exit": "Exit B - West Wing Staircase",
  "checked_at": "2026-04-23T10:10:00"
}
```

---

### 12. `POST /api/v1/query` 🔒
**Owner:** Person 3 (route) + Person 2 (AI processing) | **Used by:** ALL (Chat UI)

```
Request: QueryRequest
{
  "query": "What should I do if there's a fire in my room?",
  "session_id": "session_abc123",
  "category": "emergency_guidance"
}

Response: QueryResponse
{
  "answer": "If there's a fire in your room: 1) Alert others...",
  "sources": ["fire_safety_manual.pdf (p.12)", "hotel_protocol.pdf (p.5)"],
  "confidence": 0.92,
  "explanation": "Retrieved from fire safety protocols...",
  "cache_status": "miss",
  "response_time_ms": 1250.5,
  "session_id": "session_abc123",
  "query_log_id": 42
}
```

**Internal Flow:**
1. Person 3's `/query` route receives request
2. Checks Redis cache (Person 3)
3. If cache miss → calls `ai_core.main.process_query()` (Person 2)
4. Person 2 returns `AIProcessResponse`
5. Person 3 wraps into `QueryResponse`, caches it, logs it

---

### 13. `POST /api/v1/feedback` 🔒
**Owner:** Person 3 | **Used by:** ALL

```
Request: FeedbackCreate
{
  "target_type": "ai_response",
  "rating": "helpful",
  "comment": "Very accurate fire instructions",
  "query_log_id": 42
}

Response: FeedbackResponse
```

---

### 14. `GET /api/v1/feedback/stats` 👑
**Owner:** Person 3 | **Used by:** Admin Dashboard

```
Response: FeedbackStats
{
  "total_feedbacks": 150,
  "helpful_count": 120,
  "not_helpful_count": 30,
  "helpful_percentage": 80.0,
  "recent_comments": ["Great response!", "Needs more detail"]
}
```

---

### 15. `GET /api/v1/notifications` 🔒
**Owner:** Person 3 | **Used by:** ALL

```
Response: NotificationListResponse
{
  "notifications": [
    {
      "id": 1,
      "notification_type": "incident_alert",
      "title": "🔥 Fire reported on Floor 3",
      "message": "Fire in Room 305. Staff response needed.",
      "incident_id": 1,
      "is_read": false,
      "created_at": "2026-04-23T10:05:00"
    }
  ],
  "total": 5,
  "unread_count": 3
}
```

---

### 16. `PATCH /api/v1/notifications/{id}/read` 🔒
**Owner:** Person 3 | **Used by:** ALL

```
Response: MessageResponse
{
  "message": "Notification marked as read",
  "success": true
}
```

---

### 17. `POST /api/v1/notifications/broadcast` 👑
**Owner:** Person 3 | **Used by:** Admin only

```
Request:
{
  "title": "⚠️ Evacuation Notice",
  "message": "Please evacuate Floor 3 immediately via West Wing stairs",
  "notification_type": "broadcast"
}

Response: MessageResponse
```

---

## 🔗 Integration Points (How Persons Connect)

```
┌──────────────────────────────────────────────────────────────┐
│                        FRONTEND (ALL 3)                       │
│  Person 1: Panic Button, Dashboard                           │
│  Person 2: AI Chat UI                                        │
│  Person 3: Login, Safety Button, Feedback                     │
└────────────────────────┬─────────────────────────────────────┘
                         │ HTTP calls
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                     main.py (Person 3 owns)                   │
│  Registers all routers from all 3 persons                    │
└────┬───────────────┬──────────────────┬──────────────────────┘
     │               │                  │
     ▼               ▼                  ▼
┌─────────┐   ┌──────────┐    ┌─────────────────┐
│incidents/│   │ backend/ │    │   ai_core/      │
│ routes   │   │ api/     │    │   main.py       │
│(Person 1)│   │(Person 3)│    │  (Person 2)     │
│          │   │          │    │                 │
│ report   │   │ auth     │    │ process_query() │
│ get list │   │ query ─────────→ (RAG+Agents)  │
│ update   │   │ feedback │    │                 │
│ stats    │   │ notifs   │    │ Returns:        │
│ safety   │   │ cache    │    │ AIProcessResp   │
└────┬─────┘   └────┬─────┘    └────┬────────────┘
     │               │               │
     ▼               ▼               ▼
┌──────────────────────────────────────────────────┐
│              shared/ (ALL 3)                      │
│  schemas.py │ models.py │ enums.py │ config.py   │
│  database.py │ dependencies.py │ utils.py        │
└──────────────────────────────────────────────────┘
     │               │               │
     ▼               ▼               ▼
  PostgreSQL       Redis          FAISS Index
```

---

## ⚠️ Rules for ALL Team Members

1. **ALL request/response models** live in `shared/schemas.py` — NEVER define Pydantic models in your own files for API I/O
2. **ALL enums** live in `shared/enums.py`
3. **ALL DB models** that are used by 2+ people live in `shared/models.py`
4. **Import dependencies** from `shared/dependencies.py` (get_db, get_current_user, get_redis)
5. **Person 2 → Person 3 interface**: Person 3 calls `ai_core.main.process_query(request)` — NO direct imports of agents/rag
6. **Test with mock first**: Person 2's `main.py` ships with a mock. Person 3 integrates immediately.
7. **No cross-folder imports**: Person 1 never imports from Person 3's backend/. Use shared/ only.
