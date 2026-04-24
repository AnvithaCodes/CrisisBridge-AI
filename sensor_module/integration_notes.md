# Integration Notes — Sensor Module
## CrisisBridge AI — Cross-Module Contract

> **IMPORTANT:** This file is the contract between the isolated `sensor_module/`
> and the rest of the CrisisBridge system. Nothing in this file has been
> implemented yet. This is a guide for **Person 3** to complete the connection.

---

## 1. What This Module Provides (Already Done)

The `sensor_module` is a fully self-contained FastAPI app running on **port 8001**.
It exposes the following stable API surface:

| Endpoint             | Method | Description                          |
|:---------------------|:-------|:-------------------------------------|
| `/sensor/register`   | POST   | Register a sensor with a threshold   |
| `/sensor/list`       | GET    | List all registered sensors          |
| `/sensor/data`       | POST   | Submit a reading (triggers detection)|
| `/sensor/alerts`     | GET    | View recent alerts (admin only)      |
| `/sensor/trigger`    | POST   | Manually force a spike (demo use)    |

---

## 2. What the Main System Needs to Add

### 2.1 Incident Schema Change (`shared/schemas.py`)

The `IncidentCreate` schema must be extended to support sensor-originated incidents:

```python
# ADD these two optional fields to IncidentCreate in shared/schemas.py
source: Optional[str] = "user"          # "user" | "sensor"
sensor_id: Optional[str] = None         # e.g., "S1"
```

### 2.2 Incident Model Change (`shared/models.py`)

The `Incident` SQLAlchemy model must be extended:

```python
# ADD these two columns to the Incident model in shared/models.py
source    = Column(String, default="user")   # "user" | "sensor"
sensor_id = Column(String, nullable=True)    # e.g., "S1"
```

---

## 3. How to Connect — Integration Webhook (Person 3's Task)

When the `sensor_module` detects a spike, it can optionally call the main app's
incident endpoint. Person 3 needs to:

**Step 1:** Uncomment/enable the POST call in `sensor_module/api/routes.py`
by setting `MAIN_APP_URL` and enabling the webhook in the `/sensor/data` endpoint.

**Step 2:** The payload format the sensor module will send is:

```json
{
  "incident_type": "fire",
  "severity": "HIGH",
  "title": "Sensor Alert: fire spike in floor_3_kitchen",
  "description": "Sensor S2 reported value 95.1 exceeding threshold 80.0",
  "zone": "floor_3_kitchen",
  "source": "sensor",
  "sensor_id": "S2"
}
```

**Step 3:** The target endpoint on the main app is:
```
POST http://localhost:8000/api/v1/incidents/report
Authorization: Bearer <admin_token>
```

---

## 4. Admin Confirmation Layer (Future Enhancement)

Currently: Spikes generate alerts immediately (visible in `/sensor/alerts`).

Future design:
1. Spike detected → Alert stored in memory → **Push to admin notification** (WebSocket/polling)
2. Admin sees alert in dashboard → Clicks "Confirm Incident"
3. Only then → `POST /api/v1/incidents/report` is called

This prevents false alarms from automatically creating incidents.

---

## 5. Sensor Alerts — Admin Only

- The `/sensor/alerts` endpoint should be restricted to `role=admin` once auth is integrated.
- Add `current_user: User = Depends(get_current_admin_user)` to the route.
- The dependency `get_current_admin_user` is already defined in `shared/dependencies.py`.

---

## 6. Database (Future — Not Required Now)

Currently, all sensor data is stored **in-memory only** (intentional for MVP isolation).

If persistence is needed later:
- Add a `SensorReading` table to `shared/models.py`
- Add a `SensorAlert` table to `shared/models.py`
- Replace the in-memory list in `spike_detector.py` with DB calls

---

## 7. How to Run (Current Isolated Mode)

**Terminal 1 — Main App:**
```powershell
uvicorn main:app --reload --port 8000
```

**Terminal 2 — Sensor Module:**
```powershell
uvicorn sensor_module.main:app --reload --port 8001
```

**Terminal 3 — Simulator (optional):**
```powershell
python -m sensor_module.simulator.sensor_simulator
```
