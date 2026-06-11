# MyuKura CareOps Memory Agent

A supervised operational memory agent for clinical teams that converts approved synthetic clinical notes into reviewable operational tasks, handoffs and audit trails.

**Submission for the Google Cloud Rapid Agent Hackathon — MongoDB Partner Track**

> **⚠️ SAFETY WARNING**
>
> This project uses **synthetic demo data only**. It does not connect to real EHRs or contain real patient data.
> - **No diagnosis** is performed.
> - **No treatment** is recommended.
> - **No medication changes** are made.
> - All agent outputs require **human approval** (human-in-the-loop).
> - Simulated delivery only.

## Roadmap & Future Phases
- **Phase 1-4D**: Completed (Local FastAPI, React, MongoDB, Gemini Orchestrator, Safety Verifier, MCP Adapter, Observability Hooks).
- **Phase 5**: Cloud Run deployment + Devpost packaging.
- **Future**: Dedicated Worker service, Cloud Tasks, and Official MongoDB MCP integration.

## Target Architecture
- **Frontend**: React + Vite + TypeScript
- **API**: FastAPI (Currently runs in background simulation locally)
- **Worker**: FastAPI (Stubbed for future Cloud Tasks integration)
- **State/Memory**: MongoDB Atlas (`agent_runs`, `careops_tasks`, `mcp_tool_calls`, etc. - our core operational layer)
- **Agent**: Gemini Model Chain with Structured Extraction and Fallbacks
- **Tools**: Controlled MongoDB Tool Adapter layer (MCP-compatible contracts)
- **Observability**: Optional Arize Phoenix hooks & Dynatrace target integration (Safe, no PHI logged)

## Sensitive Data Guardrails
This project employs a sensitive-data-ready architecture:
- **Synthetic Demo Only**: The system strictly uses synthetic demographic and clinical data. It is not connected to any real EHR or patient databases.
- **Secure Storage**: MongoDB Atlas accesses are strictly scoped, and all production credentials will be managed via Google Cloud Secret Manager.
- **Redacted Telemetry**: Application logs and observability traces (Dynatrace/Arize) are redacted to exclude full clinical note text and any potential PHI/PII.
- **Future Hardening**: We have documented a roadmap integration path for Google Cloud Sensitive Data Protection (DLP) for automated pre-persistence inspection.
- **Disclaimer**: This demo makes no compliance claims and is not certified for HIPAA/GDPR compliance. It demonstrates a safety-oriented baseline architecture.

*Note on MCP: the agent's MongoDB tools are exposed through a controlled tool adapter that follows MCP-style tool contracts (named tools, structured inputs, full per-call audit logging in the `mcp_tool_calls` collection). For the public healthcare demo the adapter enforces strict scoping on every read/write instead of exposing raw database access; our evaluation of the official MongoDB MCP Server (read-only mode) is documented in `docs/OFFICIAL_MONGODB_MCP_READONLY_NOTES.md`.*

## API Endpoints (Phase 2A)
- `POST /demo/seed`: Idempotently seeds synthetic demographic records.
- `GET /mongodb/activity`: Real-time footprint of MongoDB usage.
- `POST /agent-runs`: Creates a run, persists notes, enqueues simulation.
- `GET /agent-runs`: Lists stored runs.
- `GET /agent-runs/{run_id}`: Returns run details and current status.
- `GET /agent-runs/{run_id}/events`: Returns timeline events from `agent_audit_logs`.
- `GET /tasks` & `PATCH /tasks/{task_id}/status`: Fetch and mutate operational tasks.

## Running Locally

### 1. Environment Setup
Copy `.env.example` to `.env` in the `apps/api` directory.
- `STATE_BACKEND=mongodb`: Requires a valid `MONGODB_URI` connection string to persist tasks and audit logs.
- `STATE_BACKEND=memory`: Uses purely mock data structures (good for offline testing, but won't trace MCP tools).
- `GEMINI_ENABLED=true`: Requires a valid `GEMINI_API_KEY` to run the active reasoning orchestrator. Setting to `false` gracefully disables Gemini and restricts testing to `mock` mode.

### 2. Start the API
```bash
cd apps/api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --port 8000 --reload
```
Test: `http://localhost:8000/health`

### 3. Worker Service (Stubbed)
The `apps/worker` directory contains a minimal stub. Currently, async tasks run via FastAPI `BackgroundTasks` directly in the API for simplicity of local demonstration.

### 4. Running the Main Demo
1. Start the API and Web.
2. Open `http://localhost:5173`.
3. Click "Seed Demo Data" in the top right to create baseline demographic/clinic entries.
4. Provide a synthetic clinical note.
5. Select "Gemini" or "Mock" mode and execute the Agent.
6. Observe the Task Board, Audit Timeline, and Controlled MongoDB Tools Trace.

**Current Limitations:** Not deployed yet. Polling loops are localized and not optimized for production web sockets.

### Frontend
```bash
cd apps/web
npm install
npm run dev
```
Test: `http://localhost:5173`

---

## Final Submission & Live Demo

**Live Demo URL:** `https://myukura-careops-web-1001238764138.europe-west1.run.app/`

*Note: The demo requires a backend-enforced Access Code to unlock the UI and execute the Gemini models. Please refer to your Hackathon submission notes for the code.*

**Main Features:**
*   Extraction of operational "CareOps" tasks from unstructured text and voice notes.
*   **Live persistent operational memory** powered by MongoDB Atlas.
*   Resilient Gemini model chain (gemini-3.5-flash primary with automatic fallbacks, every attempt visible in the UI) plus a local mock simulator mode.
*   Evidence Layer with system and trace transparency.

**Safety Boundaries:**
*   **No Diagnosis:** The agent strictly refuses clinical requests.
*   **Prompt-Injection Defense:** A dual-layer safety validator prevents adversarial manipulation.
*   **Input Constraints:** Strict 6,000-character and 5-minute voice ingestion limits are enforced.

**Partner Integration Status:**
*   **MongoDB (our partner track):** Live integration — operational memory, task storage, audit logs and per-call tool tracing all run on MongoDB Atlas.
*   **Arize & Elastic (roadmap, outside our track):** the outbox pattern generates redacted payloads and the export workers are implemented, but external export is intentionally **disabled** in the public demo to avoid leaking demo traffic to third-party services.
