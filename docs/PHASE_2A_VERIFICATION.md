# Phase 2A Verification Checklist

This document details the manual verification flow for the MongoDB Persistent State implementation.

## 1. Setup and Environment
1. Ensure your MongoDB Atlas cluster is active and your current IP is whitelisted (or `0.0.0.0/0` temporarily).
2. Copy `.env.example` to `.env` in `apps/api/`.
3. Set `STATE_BACKEND=mongodb`.
4. Provide the correct `MONGODB_URI` without quotation marks.

## 2. Running the Services
### API
```bash
cd apps/api
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --port 8000 --reload
```

### Worker Stub
```bash
cd apps/worker
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --port 8001 --reload
```
*(Confirm Worker remains a stub: Hitting `POST http://localhost:8001/worker/process-run` still returns a simulated Phase 1 placeholder).*

### Frontend
```bash
cd apps/web
npm install
npm run dev
```

## 3. Execution Verification
1. **Seed Demo Data**: In the UI, click "Seed Demo Data". This fires `POST /demo/seed`.
   - **Verification**: Go to Atlas and confirm `clinics`, `patients_demo`, and `professional_preferences` are seeded. Calling it a second time should not duplicate the entries (idempotency check).
2. **Create Agent Run**: Enter a synthetic note in the UI and click "Run CareOps Agent".
   - **Verification**: In Atlas, check the `source_notes` collection for the note, and `agent_runs` for the execution status.
3. **Lifecycle Progress**: Wait ~15 seconds for the mock async lifecycle to progress.
   - **Verification**: Check `agent_audit_logs` in Atlas to ensure the timeline events (e.g., `MOCK_TASKS_WRITTEN`) are recorded.
   - **Verification**: Check `careops_tasks` to ensure 4 proposed tasks were generated.
4. **Task Updates**: In the UI Task Board, click "Approve" on a task.
   - **Verification**: Check `task_status_history` in Atlas to see the transition from `proposed` to `approved`.
5. **Persistence Check**: Restart the API server (`Ctrl+C` then restart). Refresh the browser.
   - **Verification**: The Run ID, task board, and timeline will immediately reload their state from MongoDB, proving persistence.

## 4. Structured Error Smoke Checks
- **Validation Check**: Paste a source note larger than 6000 characters. Expect a `VALIDATION_ERROR` or `INPUT_TOO_LARGE` via UI alert.
- **Connection Check**: Deliberately set `MONGODB_URI` to a broken string and start the API. Expect a `MONGODB_CONNECTION_ERROR` structured exception.
- **Run Not Found Check**: Trigger `GET http://localhost:8000/agent-runs/fake-run`. Expect a `RUN_NOT_FOUND` structured response.
- **Invalid Transition**: Attempt to patch a `done` task to `proposed` using Postman/cURL. Expect an `INVALID_STATUS_TRANSITION` 400 error.

## 5. Exclusions Confirmed
- No Gemini models are implemented.
- No MongoDB MCP tools are configured.
- No Google Cloud Tasks exist (using FastAPI BackgroundTasks).
