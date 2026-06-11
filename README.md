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

## Architecture

- **Frontend**: React + Vite + TypeScript
- **API**: FastAPI on Cloud Run (background task queue for async agent runs)
- **Worker**: FastAPI stub (prepared for future Cloud Tasks integration)
- **State/Memory**: MongoDB Atlas (`agent_runs`, `careops_tasks`, `mcp_tool_calls`, etc.)
- **Agent**: Gemini Model Chain with Structured Extraction and Fallbacks
- **Tools**: Official MongoDB MCP Server (read-only, operational memory reads) + Controlled MongoDB Tool Adapter layer (scoped writes, per-call audit logging)
- **Observability**: Optional Arize Phoenix hooks & Dynatrace target integration (safe, no PHI logged)

## Sensitive Data Guardrails

- **Synthetic Demo Only**: Strictly synthetic demographic and clinical data. Not connected to any real EHR.
- **Secure Storage**: MongoDB Atlas credentials managed via Google Cloud Secret Manager.
- **Redacted Telemetry**: Application logs and traces are redacted to exclude clinical note text and any potential PHI/PII.
- **Future Hardening**: Documented roadmap for Google Cloud Sensitive Data Protection (DLP) integration.
- **Disclaimer**: This demo makes no compliance claims (HIPAA/GDPR). It demonstrates a safety-oriented baseline architecture.

*Note on MCP: operational memory reads run through the **official MongoDB MCP Server** (`mongodb-mcp-server`, spawned over stdio, always with `--readOnly`) when `MONGODB_MCP_ENABLED=true`. If the MCP server is unavailable, the agent falls back to the controlled native adapter and records the fallback in the audit trail. Writes never go through MCP.*

## API Endpoints

| Method  | Path                                 | Auth | Description |
|---------|--------------------------------------|------|-------------|
| `GET`   | `/health`                            | No   | Health probe (Cloud Run / load balancer) |
| `POST`  | `/demo/seed`                         | Yes  | Idempotently seed synthetic demographic records |
| `GET`   | `/mongodb/activity`                  | Yes  | Real-time MongoDB usage footprint |
| `POST`  | `/agent-runs`                        | Yes  | Create a run, persist notes, enqueue processing |
| `GET`   | `/agent-runs`                        | Yes  | List stored runs |
| `GET`   | `/agent-runs/{run_id}`               | Yes  | Run details and current status |
| `GET`   | `/agent-runs/{run_id}/events`        | Yes  | Audit timeline events |
| `GET`   | `/agent-runs/{run_id}/mcp-tool-calls`| Yes  | MCP tool call trace |
| `GET`   | `/tasks`                             | Yes  | List operational tasks |
| `PATCH` | `/tasks/{task_id}/status`            | Yes  | Update task status (approve/reject) |
| `GET`   | `/mcp/tool-calls`                    | Yes  | List all MCP tool calls |

All protected endpoints require the `x-demo-access-code` header.

## Running Locally

### Prerequisites

- Python 3.11+
- Node.js 20+ (for the frontend)
- MongoDB Atlas account (for `mongodb` backend) or use `memory` backend for offline testing

### 1. API Setup

```bash
cd apps/api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env — set DEMO_ACCESS_CODE, and optionally MONGODB_URI / GEMINI_API_KEY
uvicorn app.main:app --port 8000 --reload
```

Verify: `curl http://localhost:8000/health`

### 2. Frontend Setup

```bash
cd apps/web
npm ci
npm run dev
```

Open: `http://localhost:5173`

### 3. Seed Demo Data

With the API running:

```bash
python scripts/seed_demo_data.py --access-code YOUR_CODE
```

Or via the UI: click **"Seed Demo Data"** in the top-right corner.

### 4. Run the Demo

1. Open `http://localhost:5173`
2. Enter the demo access code
3. Provide a synthetic clinical note
4. Select **"Gemini"** or **"Deterministic"** mode and execute the Agent
5. Observe the Task Board, Audit Timeline, and MCP Tool Trace

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `STATE_BACKEND` | Yes | `memory` (offline) or `mongodb` (Atlas) |
| `DEMO_ACCESS_CODE` | Yes | Access code for protected endpoints |
| `MONGODB_URI` | If `mongodb` | MongoDB Atlas connection string |
| `GEMINI_ENABLED` | No | `true` to enable Gemini AI extraction |
| `GEMINI_API_KEY` | If Gemini | Google AI Studio API key |
| `GEMINI_PRIMARY_MODEL` | If Gemini | e.g. `gemini-3.5-flash` |
| `GEMINI_FALLBACK_MODELS` | If Gemini | e.g. `gemini-3.1-flash-lite,gemini-2.0-flash` |
| `GEMINI_MAX_MODEL_ATTEMPTS` | Number | e.g. `3` |

See [`.env.example`](.env.example) for the full list.

---

## Live Demo

**Live Demo URL:** `https://myukura-careops-web-1001238764138.europe-west1.run.app/`

*The demo requires a backend-enforced Access Code. Refer to your Hackathon submission notes for the code.*

## Key Features

* Extraction of operational "CareOps" tasks from unstructured text and voice notes.
* **Live persistent operational memory** powered by MongoDB Atlas, read through the **official MongoDB MCP Server** (read-only) on every run.
* Resilient Gemini model chain (gemini-3.5-flash primary with automatic fallbacks, every attempt visible in the UI) plus a deterministic keyword-matching extractor as fallback.
* Evidence Layer with system and trace transparency.

## Safety Boundaries

* **No Diagnosis:** The agent strictly refuses clinical requests.
* **Prompt-Injection Defense:** A dual-layer safety validator prevents adversarial manipulation.
* **Input Constraints:** Strict 6,000-character and 5-minute voice ingestion limits are enforced.

## Partner Integration Status

* **MongoDB (partner track):** Live integration — operational memory, task storage, audit logs and per-call tool tracing all run on MongoDB Atlas.
* **Arize & Elastic (roadmap):** The outbox pattern generates redacted payloads and the export workers are implemented, but external export is intentionally **disabled** in the public demo.

## License

[MIT](LICENSE)
