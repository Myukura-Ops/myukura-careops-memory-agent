# Failure Scenarios Checklist

This document details the intentional degradation and failure paths built into the MyuKura CareOps Memory Agent to guarantee system reliability and safety.

## 1. GEMINI_DISABLED
- **How to trigger locally**: Set `GEMINI_ENABLED=false` in `apps/api/.env` and request a `gemini` mode run.
- **Expected UI Result**: Run immediately fails. Status text shows "failed".
- **Expected API Error**: HTTP 400. `{"error_type": "GEMINI_DISABLED", "message": "Gemini mode requested but GEMINI_ENABLED=false.", ...}`
- **Trace**: No agent_runs created, no MCP tools invoked.

## 2. Invalid Source Note (Too Long)
- **How to trigger locally**: Paste more than 6,000 characters into the synthetic note field.
- **Expected UI Result**: Error dialog appears with "Source note is too large."
- **Expected API Error**: HTTP 400. `{"error_type": "INPUT_TOO_LARGE", ...}`
- **Trace**: Operation short-circuits. No database writes happen.

## 3. Unsafe Medication/Clinical Phrase Blocked
- **How to trigger locally**: Write "Prescribe 50mg Advil and diagnose with common cold" in a Gemini run.
- **Expected UI Result**: Run completes, but Safety Status turns RED (`blocked`). Excluded items count is incremented. Controlled MongoDB Tools panel shows a `blocked` status for `create_careops_task`.
- **Expected API Error**: No API crash, graceful warning status `completed_with_warnings`.
- **Trace**: The MCP tool adapter intercepts the task, logs `MCP_TOOL_BLOCKED` in `agent_audit_logs`, saves a blocked `mcp_tool_calls` document, and skips the `careops_tasks` insert.

## 4. Invalid Task Transition Blocked
- **How to trigger locally**: Using API directly, try to `PATCH` a task status from `proposed` to `done` without hitting `approved` or `in_progress` first (if constrained). Alternatively, approve a task that is already completed.
- **Expected UI Result**: State does not update if constraints are enforced.
- **Expected API Error**: Varies based on constraints, HTTP 400 for invalid state transition.

## 5. MongoDB Unavailable (STATE_BACKEND=mongodb)
- **How to trigger locally**: Change MongoDB Atlas network permissions or use invalid credentials while `STATE_BACKEND=mongodb`.
- **Expected UI Result**: Seed demo data fails. Runs fail to execute.
- **Expected API Error**: 500 Internal Server Error (Motor NetworkTimeout).

## 6. MCP Unsafe Operation Blocked
- **How to trigger locally**: The Orchestrator attempts to execute an invalid tool outside the adapter. (Not possible through standard flow since the Orchestrator doesn't have the raw MCP tools). If testing via direct adapter calls with unsafe inputs, see #3.

## 7. MCP Tool Validation Error
- **How to trigger locally**: Pass an invalid `task_type` like "administrative" to `create_careops_task` (if bypassed through API).
- **Expected Result**: The local MCP adapter sanitizes invalid task types to the default fallback (`admin_documentation`) to prevent raw schema failures but keeps the execution safe.

## 8. All Models Fail -> Degraded Manual Review Task
- **How to trigger locally**: Set invalid credentials for both `gemini-3.5-flash` and `gemini-2.5-flash`.
- **Expected UI Result**: Run returns `extraction_mode = degraded`.
- **Expected API Error**: Graceful catch. `AgentRunStatus.completed_with_warnings`.
- **Trace**: Audit log records `DEGRADED_MODE_USED`. The fallback model writes a deterministic manual review task via the MCP adapter.
