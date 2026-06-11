# Dynatrace Access & Integration Checklist

This document tracks the actual configuration and integration of Dynatrace via OpenTelemetry, which serves as our final observability integration target for the hackathon evidence pack.

**Current Status:** `trial_available_pending_signup`

## Status Values
- `not_checked`
- `trial_available_pending_signup`
- `access_confirmed`
- `smoke_test_passed`
- `unavailable`
- `deferred`

## Checklist

- [ ] Sign up for Dynatrace free trial from the hackathon resources.
- [ ] Create or access Dynatrace tenant.
- [ ] Locate OTLP ingest endpoint.
- [ ] Create API token with ingest permissions.
- [ ] Configure local private `.env`:
  ```env
  DYNATRACE_ENABLED=true
  OBSERVABILITY_ENABLED=true
  OBSERVABILITY_PROVIDER=dynatrace
  OTEL_EXPORTER_OTLP_ENDPOINT=<private_endpoint>
  OTEL_EXPORTER_OTLP_HEADERS=Authorization=Api-Token <private_token>
  OTEL_SERVICE_NAME=myukura-careops-memory-agent
  ```
- [ ] Run local API.
- [ ] Trigger mock run.
- [ ] Trigger Gemini disabled path.
- [ ] Trigger MCP tool call.
- [ ] Confirm traces/logs/metrics appear in Dynatrace.
- [ ] Capture screenshot for Devpost.
- [ ] If successful, update status to `smoke_test_passed`.
