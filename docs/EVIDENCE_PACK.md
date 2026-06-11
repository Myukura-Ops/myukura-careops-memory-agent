# Evidence Pack for Judges

This document outlines the specific features and artifacts judges should evaluate to confirm the successful implementation of the operational memory architecture.

## 1. MongoDB Atlas Collections
The application utilizes MongoDB Atlas as the central nervous system. Judges can verify the existence and structure of the following active collections:

- `clinics`
- `patients_demo` (Excludes `demographic_summary` to enforce safety boundaries)
- `professional_preferences`
- `source_notes`
- `agent_runs`
- `agent_audit_logs`
- `careops_tasks`
- `task_status_history`
- `mcp_tool_calls`

## 2. Screenshot & Video Checklist
Judges should look for these visual proofs:
- [ ] **Task Board Lifecycle**: Tasks moving from `proposed` to `approved` to `in_progress` to `done`.
- [ ] **Audit Timeline**: Logs appearing in chronological order matching the execution.
- [x] **Controlled MongoDB Tools Panel** (Shows safe tool logs tracing back to db operations).
- [x] **Safety Banners** (Synthetic mode clearly visible, Phase 4D tagged).
- [x] **Blocked Action Trace** (Demonstrating what happens when an unsafe "prescribe" input is intercepted by the adapter).
- [x] **Observability Badge** (Shows Arize and Dynatrace readiness status).
- [ ] **MongoDB Activity Counter**: Showing the number of writes correctly increasing with each action.
- [ ] **Blocked Action Evidence**: (Video/Screenshot) of an unsafe query (e.g. "prescribe advil") resulting in a RED `blocked` tool call and a `completed_with_warnings` status.

## 3. Dynatrace Evidence Target
*Current status: pending trial access*
- [ ] OTLP endpoint configured
- [ ] Trace visible for agent run
- [ ] Trace visible for model attempt
- [ ] Trace visible for MCP tool call
- [ ] Error/degraded mode trace
- [ ] Screenshot captured

## 4. Technical Evidence
- **STATE_BACKEND**: Configured to `mongodb`.
- **Motor Async Driver**: Demonstrates non-blocking I/O within the FastAPI event loop.
- **Document IDs**: The UI surfaces real `_id`, `task_id`, and `tool_call_id` properties directly from MongoDB.
- **Controlled Traceability**: We chose a direct API->MongoDB layer for trace execution rather than a black-box MCP connection, ensuring maximum visibility and strict clinical safety.
- **Sensitive-Data-Ready Architecture**: 
  - Synthetic demo data only (No HIPAA/GDPR claims).
  - Secret Manager integration planned.
  - Redacted logs and traces (no PHI/PII emitted).
  - Future path documented for Google Cloud Sensitive Data Protection (DLP).
- **Controlled Tool Adapter**: All database modifications from the model pass through a strictly typed `mcp_tool_adapter` to prevent raw query vulnerabilities.
- **API Endpoints**: Over 10 active endpoints including `GET /mcp/tool-calls` and `GET /mongodb/activity`.
- **Worker Stub**: The `careops-worker` microservice is intentionally deferred to Phase 5 Cloud deployment to keep the local demo cohesive.
- **Public API Access**: Public `/health` endpoint verified active.
- **Org Policy Exception**: Temporary project-level override applied and documented.
- **Synthetic-data-only**: Guardrails remain strictly active to safely permit this public exception.

## 3. UI Evidence
The frontend application (`localhost:5173`) exposes:
- **Run CareOps Agent Button**: Triggers the `POST /agent-runs` mutation.
- **Status Lifecycle**: Visually transitions through `queued`, `processing`, `model_running`, etc.
- **Persistent Audit Timeline**: Fetched and polled directly from `agent_audit_logs`.
- **Persistent Task Board**: Interactive Kanban-style board polling from `careops_tasks`.
- **Task Controls**: End-user controls to transition statuses (`Approve`, `Start Work`, `Mark Done`).
- **MongoDB Activity Panel**: Real-time readouts of collection footprint and write counts.

## 4. Safety Evidence
This project strictly enforces:
- **Synthetic Demo Data**: No real patient PHI/PII is used.
- **No Diagnosis/Treatment Recommendations**: The system generates administrative/operational tasks only (e.g., "follow_up_scheduling").
- **Deterministic Safety Verifier**: Actively intercepts tool calls containing blocked terms (like "diagnose", "prescribe", "dosage").
- **Human-in-the-Loop**: All generated tasks require explicit human approval.
- **No Real Delivery**: Webhooks, emails, and EHR connections are simulated.
- **Tool Boundary Restrictions**: We deliberately created a controlled adapter instead of connecting the official MongoDB MCP server to the runtime to prevent raw database exposure.
