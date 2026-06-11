# Arize Phoenix Observability

This document details the optional observability integration layer for Arize Phoenix.

## Purpose
Arize Phoenix can be used as an agent trace observability layer to understand how the Gemini Model Chain executes, safely inspect latency, model fallbacks, and the outcome of the deterministic safety verifiers without exposing raw clinical data.

**Status:** The observability abstraction has been implemented with "no-op" logging hooks. The full dependency (OpenInference) is deferred to prevent breaking the core hackathon demo. 

## Configuration
To enable Arize Phoenix logging, set the following environment variables in your `.env` file:
```env
OBSERVABILITY_ENABLED=true
ARIZE_ENABLED=true
ARIZE_PROJECT_NAME=myukura-careops-memory-agent
ARIZE_API_KEY=YOUR_API_KEY
ARIZE_SPACE_ID=YOUR_SPACE_ID
PHOENIX_COLLECTOR_ENDPOINT=https://app.phoenix.arize.com/v1/traces
```

## Privacy & Safety Policy
The observability layer is bound by the same strict constraints as the MongoDB MCP Tool layer.
**What is Safe to Trace:**
- Model IDs (e.g., `gemini-3.5-flash`)
- Latency (ms)
- Status (`success`, `failed`, `timeout`, `invalid_json`)
- Block counts (e.g., "Safety Blocked: 2")
- Safe tool names (e.g., `create_careops_task`, `search_patient_memory`)

**What is NEVER Traced:**
- The full `source_note` clinical context.
- Patient/Clinic demographics in raw form.
- Full text output from the Gemini model before redaction.

## Hook Placements
The application uses a unified `observability.py` service. Calls are wrapped in `try/except` to ensure they are best-effort and never block the agent run.
- **Agent Run Lifecycle:** `trace_agent_run_started`, `trace_agent_run_completed`
- **Model Executions:** `trace_model_attempt`
- **Safety Verifier:** `trace_safety_result`
- **MCP Tools:** `trace_mcp_tool_call`
- **Fallback:** `trace_degraded_mode_used`
