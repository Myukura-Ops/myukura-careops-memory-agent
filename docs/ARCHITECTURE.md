# Architecture

## Target Architecture
The system uses an asynchronous request-reply pipeline to keep the frontend responsive during potentially long agent runs.

### Phase 1 Implemented Architecture
In Phase 1, the architecture simulates an asynchronous runtime without requiring complex infrastructure:
- **API Service**: Handles HTTP endpoints. Uses a temporary `in_memory_agent_runs` repository for state sharing.
- **Mock Queue**: Uses FastAPI `BackgroundTasks` as a placeholder for Cloud Tasks.
- **Worker Stub**: The `careops-worker` service is deployed but its logic runs inside the API's background tasks during Phase 1 due to the in-memory shared state constraint.
- **Simulated Agent Lifecycle**: An `agent_run_simulator` simulates delays and state transitions of the future AI agent.

### Phase Transition / Replacement Plan
- **Phase 2**: Replace `in_memory_agent_runs` with MongoDB persistence.
- **Phase 2/3**: Replace `mock_queue` with Google Cloud Tasks, routing payloads to the real Worker.
- **Phase 3**: Replace `agent_run_simulator` mock model steps with a real Gemini fallback model chain.
- **Phase 4**: Add MongoDB MCP/tools integration to the Worker's agent execution logic.

### Target Flow (Phase 2+)
1. `POST /agent-runs` to API.
2. API creates a run record in MongoDB.
3. API enqueues a job via Cloud Tasks.
4. Cloud Tasks invokes the Worker service.
5. Worker processes the agent steps (Gemini, MCP).
6. Worker updates MongoDB state.
7. Frontend UI polls API or uses WebSockets for status updates.

## Services
- **careops-api**: FastAPI service for the web frontend to create runs and fetch state.
- **careops-worker**: FastAPI service that executes the long-running agent logic.
- **careops-web**: React + Vite + TypeScript frontend.

## Target MongoDB Collections
- `clinics`
- `patients_demo` (synthetic only)
- `source_notes`
- `careops_tasks`
- `agent_runs`
- `agent_audit_logs`
- `handoff_summaries`
- `professional_preferences`
- `task_status_history`

## Agent Run States
- `queued`
- `processing`
- `model_running`
- `verifying`
- `writing_tasks`
- `waiting_human_review`
- `completed`
- `completed_with_warnings`
- `failed`

## Error Taxonomy
- `MODEL_TIMEOUT`
- `MODEL_RATE_LIMIT`
- `MODEL_INVALID_JSON`
- `MODEL_SAFETY_BLOCKED`
- `MONGODB_CONNECTION_ERROR`
- `MONGODB_WRITE_FAILED`
- `MCP_TOOL_ERROR`
- `VALIDATION_ERROR`
- `INPUT_TOO_LARGE`
- `AUTH_FAILED`
- `UNKNOWN_ERROR`
