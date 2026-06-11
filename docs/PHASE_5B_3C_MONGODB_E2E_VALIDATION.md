# Phase 5B.3c: MongoDB Agent Run End-to-End Cloud Validation

## 1. Summary
- Backend cloud API is now fully connected to MongoDB Atlas.
- Agent run lifecycle works end-to-end using mock mode.
- Human-in-the-loop task approval works.
- State persists in MongoDB.

## 2. Infrastructure Used
- **Cloud Run API**: `myukura-careops-api`
- **Region**: `europe-west1`
- **MongoDB Atlas cluster**: `myukura-careops-cluster`
- **Static egress IP**: `34.140.56.8`
- **VPC connector**: `careops-vpc`
- **Cloud Router**: `careops-router`
- **Cloud NAT**: `careops-nat`
- **Secret Manager**: `MYUKURA_MONGODB_URI`
- **Org policy public demo exception documented separately**

## 3. Code Changes Made During this Phase
During this phase, validation errors occurred due to Pydantic expecting specific formats but receiving MongoDB `ObjectId` types. The following adjustments were made:
- Added `doc.pop("_id", None)` (or `result.pop("_id", None)`) before Pydantic model creation to strip `_id` and allow safe initialization.
- Re-implemented the missing `update_run(run_id, run)` function in `mongodb_agent_runs.py` which had been left out during the initial repository migration.

Files changed:
- `apps/api/app/repositories/mongodb_agent_runs.py`
- `apps/api/app/repositories/mongodb_tasks.py`
- `apps/api/app/repositories/mongodb_source_notes.py`
- `apps/api/app/repositories/mongodb_mcp_tool_calls.py`

**Security Confirmations:**
- No secrets were added to code.
- No real patient data was used.

## 4. API Evidence
### `/health` Response
```json
{
  "status": "healthy",
  "app_env": "demo",
  "runtime": "cloud_run",
  "state_backend": "mongodb",
  "demo_mode": true,
  "gemini_enabled": false,
  "observability_enabled": false,
  "mongodb_status": "not_checked"
}
```

### `POST /agent-runs/` Response
```json
{
  "run_id": "a0378719-505d-42e1-bcd0-28e2e99b187e",
  "status": "queued",
  "message": "Agent run created and queued successfully.",
  "created_at": "2026-06-08T12:44:29.592344Z",
  "updated_at": "2026-06-08T12:44:29.592344Z"
}
```

### `GET /agent-runs/{run_id}` Final Summary
```json
{
  "run_id": "a0378719-505d-42e1-bcd0-28e2e99b187e",
  "status": "waiting_human_review",
  "execution_mode": "mock",
  "state_backend": "mongodb",
  "result": {
    "tasks_created": 4,
    "audit_events_created": 9,
    "safety_status": "passed_mock"
  }
}
```

### Audit Event Details
- Count: **7 events**
- Key Event Types:
  - `AGENT_RUN_CREATED`
  - `WORKER_SIMULATION_STARTED`
  - `MOCK_MODEL_STARTED`
  - `MOCK_SAFETY_VERIFIER_PASSED`
  - `MOCK_TASKS_WRITTEN`
  - `HUMAN_REVIEW_REQUIRED`
  - `RUN_COMPLETED`

### Task Details
- Count: **4 tasks**
- Sample Task:
```json
{
  "task_id": "d1c4cf1b-1be9-4518-84a3-148c8e4caffd",
  "title": "Schedule follow-up appointment",
  "description": "Auto-generated mock task for follow_up_scheduling",
  "status": "proposed",
  "requires_human_approval": true,
  "risk_level": "low"
}
```

### Task Approval Response
```json
{
  "task_id": "d1c4cf1b-1be9-4518-84a3-148c8e4caffd",
  "status": "approved",
  "updated_at": "2026-06-08T12:45:33.482000"
}
```

### `/mongodb/activity` Response
```json
{
  "backend": "mongodb",
  "latest_run_id": "a0378719-505d-42e1-bcd0-28e2e99b187e",
  "collections_touched": [
    "patients_demo", "task_status_history", "professional_preferences",
    "agent_runs", "careops_tasks", "clinics", "source_notes", "agent_audit_logs"
  ],
  "write_counts": {
    "agent_runs": 3,
    "careops_tasks": 8,
    "agent_audit_logs": 12,
    "task_status_history": 9
  },
  "total_writes": 38
}
```

## 5. Safety Confirmation
- Synthetic data only.
- No diagnosis.
- No treatment recommendations.
- No medication changes.
- Human approval required.
- Gemini disabled.
- No Web deployed.
- No secrets printed.
- No `0.0.0.0/0` Atlas allowlist.

## 6. Known Limitations
- `mcp_tool_calls` is empty in mock mode; this is acceptable.
- Gemini mode still pending.
- Web frontend deployment still pending.
- Password rotation for `careops_app_user` remains mandatory before final submission because URI was visible in local terminal during setup.

## 7. Next Recommended Phase
**Phase 5B.4:**
- Web frontend Cloud Run deployment using exact API URL.
- CORS validation.
- UI end-to-end test against MongoDB backend.
- No Gemini yet unless architect approves.
