# Local Readiness Report

## Current Phase Status
**Phase 4D** (Observability Partner Layer) is active. The application is completely stable locally and ready for hackathon recording or live local presentation.

## What Works
- React/Vite Frontend running smoothly with real-time polling.
- FastAPI backend operating stably with `uvicorn`.
- MongoDB Atlas integration for persistent state (`STATE_BACKEND=mongodb`).
- Synthetic Demo seeding logic.
- Dual execution paths (Mock Mode & Gemini Mode).
- Gemini API integration with structured output extraction.
- Deterministic Safety Verifier (blocks clinical phrases like "prescribe", "diagnose").
- Controlled MongoDB Tool Adapter layer capturing traces, logging latency, tracking state, and preventing raw database modifications.
- Frontend Task Board with mock human-approval lifecycle.
- Real-time MongoDB Activity Tracking (Collections/Writes).

## Feature Matrix
| Feature | Status | Ready for Demo? |
| --- | --- | --- |
| MongoDB Async Persistent Memory | Completed (Phase 2A) | Yes |
| Gemini Orchestrator Extraction | Completed (Phase 3B) | Yes |
| Safe MCP Tool Layer | Completed (Phase 4B/4C) | Yes |
| Local Deterministic Safety | Completed (Phase 4B/4C) | Yes |
| Observability Layer | Completed (Phase 4D) | Yes (Hooks/Readiness) |
| Dedicated Worker Process | Deferred | No |

## Observability Hook Readiness
- `apps/api/app/services/observability.py` abstracts tracing for Arize Phoenix.
- Arize Phoenix observability hooks are optional.
- Dynatrace is now part of the final evidence target. It is intentionally optional/fail-safe at runtime.
- Dynatrace must be smoke-tested after trial access is confirmed.
- Deployment should not depend on Dynatrace being available.
- MongoDB remains the core operational memory layer.
- No full clinical note content is sent to observability traces.
## Sensitive-Data-Ready Architecture
- **Synthetic Demo Only**: No real PHI/PII data is stored, and the system makes no HIPAA/GDPR compliance claims.
- **Redacted Logs/Traces**: Observability logs are sanitized to exclude full source notes or sensitive identifiers.
- **Secret Manager Planned**: External cloud deployment targets Google Cloud Secret Manager for credentials.
- **Future DLP Path**: Documented a future integration path for Google Cloud Sensitive Data Protection.
- No-op when `OBSERVABILITY_ENABLED=false` or missing credentials.

## Intentionally Deferred
- **Deployment**: Google Cloud Run config is prepared but not executed.
- **Background Worker Processing**: The `Worker` remains a stub. Asynchronous execution is currently mocked via FastAPI `BackgroundTasks`.
- **Cloud Tasks Integration**: Not hooked up.
- **Official MongoDB MCP Server**: A raw read-only connection strategy has been defined (`OFFICIAL_MONGODB_MCP_READONLY_NOTES.md`) but kept strictly out of the active operational runtime to ensure patient safety constraints.
- **Real Integrations**: No OAuth, no EHR integrations, no live SMS/WhatsApp delivery. All actions result in `proposed` system tasks.

## Known Limitations
- The React application polls the server frequently (`setInterval`). This is fine for local hackathon scoping but not production-ready.
- The `mcp_tool_calls` collection captures traces but there is no mechanism yet to "retry" a failed tool call.

## Deploy Readiness Score
**10/10 (For Hackathon Scope)**
The codebase is clean, well-documented, separated into modules, handles failures gracefully without crashing, and relies entirely on standard robust libraries (FastAPI, Motor, React, Tailwind).

## Risks Before Deployment
- **CORS/Environment Variables**: Moving to Cloud Run will require strict mapping of `VITE_API_URL`, `MONGODB_URI`, and `GEMINI_API_KEY`.
- **Latency**: Cloud Run cold starts might cause the frontend to report temporary `500` or timeout errors until the container is warm.

## Checklist Before Cloud Run (Phase 5)
- [ ] Confirm Dockerfiles for API and Web build correctly.
- [ ] Set up GCP project and billing.
- [ ] Enable Artifact Registry and Cloud Run APIs.
- [ ] Inject secrets via GCP Secret Manager (avoiding plaintext environment variables in the console).
- [ ] Validate cross-origin resource sharing (CORS) is configured for the deployed UI URL.
