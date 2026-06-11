# Phase 3B Verification Checklist

This document details the manual verification flow for the Gemini Structured Extraction pipeline and Fallback Chain.

## 1. Setup and Environment
Ensure `.env` in `apps/api/` is properly configured:
```env
STATE_BACKEND=mongodb
MONGODB_URI=<your-cluster-uri>

GEMINI_ENABLED=false
# Only when GEMINI_ENABLED=true and a key is present will Gemini mode work.
GEMINI_API_KEY=<your-gemini-key>
```

Start the services (API, Worker, Web).

## 2. Test Scenarios

### Scenario 1: Mock Mode Works
1. Keep `GEMINI_ENABLED=false` or `true`.
2. In the UI, set Mode to **Mock**.
3. Run the agent.
4. **Expected:** Agent runs the simulated delay pipeline, generates 4 mock tasks, and succeeds.

### Scenario 2: Gemini Mode Disabled
1. Keep `GEMINI_ENABLED=false`.
2. In the UI, set Mode to **Gemini**.
3. Run the agent.
4. **Expected:** Immediate UI alert with error: `GEMINI_DISABLED: Gemini mode requested but GEMINI_ENABLED=false.`

### Scenario 3: Gemini Happy Path
1. Set `GEMINI_ENABLED=true` and restart the API.
2. Ensure you have a valid `GEMINI_API_KEY`.
3. Enter an administrative note: "Patient needs follow up scheduling and a missing release form signed."
4. Select Mode **Gemini**.
5. Run the agent.
6. **Expected:** Gemini orchestrator runs, returns JSON, tasks are proposed.

### Scenario 4: Diagnosis Exclusion
1. Run Gemini mode with note: "Patient diagnosed with type 2 diabetes. Start metformin 500mg."
2. **Expected:** The `excluded_items` counter should be > 0. The audit log should flag `SAFETY_VERIFIER_BLOCKED`. Status should be `completed_with_warnings`. No clinical tasks should appear in the board.

### Scenario 5: Missing Key / Primary Model Failure (Fallback Test)
1. Provide a broken API key (e.g. `GEMINI_API_KEY=broken`).
2. Run Gemini mode.
3. **Expected:** `execute_model_chain` tries primary model, gets a failure (403/401). Tries secondary fallback (`gemini-2.5-flash`), fails. Triggers degraded mode. Status `completed_with_warnings`. 1 Task appears: "Manual review required".

### Scenario 6: Invalid JSON (Validation Test)
*(Can be simulated by modifying `gemini_orchestrator.py` to strip JSON braces before parsing).*
**Expected:** SDK structured validation catches the error, marks attempt as `invalid_json`, and triggers fallback or degraded mode.

### Scenario 7: State Persistence
1. Refresh the browser mid-run.
2. **Expected:** Polling resumes, Audit timeline continues.

### Scenario 8: Task Board Controls
1. Approve a Gemini-generated task.
2. **Expected:** Task transitions to `approved`, and `task_status_history` is written to MongoDB.
