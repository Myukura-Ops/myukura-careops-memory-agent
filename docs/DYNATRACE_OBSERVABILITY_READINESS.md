# Dynatrace & OpenTelemetry Target Integration

This document outlines the cloud observability strategy for Dynatrace, specifically targeting our final hackathon evidence pack and future Google Cloud Run deployments of the MyuKura CareOps Memory Agent.

## Purpose
While MongoDB serves as our core operational memory and logging system, Dynatrace (via OpenTelemetry) is our planned real OpenTelemetry integration target. It provides insights into container health, latency across microservices, model invocation tracing, and high-level platform stability.

**Status:** Target Integration Mode. Dynatrace is configured as the intended target via `observability.py` hooks, guarded by try/except. Traces are explicitly built to support OTLP exporters but remain optional and fail-safe at runtime. We are pending trial signup to complete the smoke test.

## Architecture & OpenTelemetry Plan
When deployed to Google Cloud Run, the API can export traces using standard OTLP over HTTP/gRPC.

### Proposed Environment Variables
```env
DYNATRACE_ENABLED=true
OTEL_EXPORTER_OTLP_ENDPOINT=https://{your-tenant}.live.dynatrace.com/api/v2/otlp
OTEL_EXPORTER_OTLP_HEADERS=Authorization=Api-Token {DT_API_TOKEN}
OTEL_SERVICE_NAME=myukura-careops-memory-agent
OTEL_RESOURCE_ATTRIBUTES=deployment.environment=demo
```

### Key Metrics and Spans to Capture
If fully instrumented, we will export:
- **Request Latency:** API endpoints (e.g., `POST /agent-runs`).
- **Gemini Model Latency:** External API calls to Google Gen AI.
- **Fallback Metrics:** Count of primary vs. fallback model invocations.
- **Safety Blocks:** Count of tasks intercepted by `safety_verifier.py`.
- **MCP Tool Latency:** Database interactions handled by `mcp_tool_adapter.py`.
- **Degraded Mode Used:** Spikes in fallback exhaustion.

## Privacy Constraints
Similar to our internal logging:
1. No PHI, PII, or raw clinical notes will be passed into OTel Span attributes.
2. Only request metadata (latency, status codes, endpoints) and controlled safe strings (e.g., `task_type: follow_up_scheduling`) are allowed.
