# Final Local Demo Flow

This document details the exact sequence for presenting the MyuKura CareOps Memory Agent local demo.

## Prerequisites
- MongoDB Atlas cluster running and network access granted.
- `apps/api/.env` configured with `GEMINI_ENABLED=true` and a valid API key, `STATE_BACKEND=mongodb`, and `MONGODB_URI`.
- `apps/web/.env` configured if necessary (default API points to `http://localhost:8000`).

## Demo Sequence

**Step 1: Start Services**
- Terminal 1: Run the API Server
  ```bash
  cd apps/api
  uv run python -m uvicorn app.main:app --port 8000
  ```
- Terminal 2: Run the React Frontend
  ```bash
  cd apps/web
  npm run dev
  ```
- Open browser at `http://localhost:5173`.

**Step 2: Database Setup & Evidence of Safety**
- Show the Safety Banner at the bottom of the screen (Synthetic Demo Only, Human Approval Required, Phase 4C).
- Click **"Seed Demo Data"** to write synthetic baseline data (Clinic, Patient, Professional) to MongoDB.

**Step 3: Baseline Mock Run**
- In the **Mode** dropdown, select **Mock**.
- Click **Run CareOps Agent**.
- Explain that mock mode provides a rapid deterministic demonstration without calling external LLMs, inserting baseline tasks into the Task Board and events into the Audit Timeline.

**Step 4: Gemini Disabled Test (Failure Scenario)**
- *Pre-demo step:* Temporarily set `GEMINI_ENABLED=false` and restart API.
- Select **Gemini** mode and hit **Run**.
- Show the graceful `GEMINI_DISABLED` failure on the UI to demonstrate environmental feature gating.
- *Restore `GEMINI_ENABLED=true` and restart API.*

**Step 5: Full Gemini Orchestrator Run**
- Change Mode to **Gemini**.
- Keep the default safe source note.
- Click **Run CareOps Agent**.
- Talk through the Audit Timeline as events appear (Started -> Context Loaded -> Extracting -> Verifier Passed -> Tools Succeeded -> Tasks Written).

**Step 6: UI Traceability & Tool Contracts**
- Point out the **Controlled MongoDB Tools** panel.
- Emphasize the adapter type: `controlled_local_adapter`.
- Explain the MCP-compatible tool contracts (`search_patient_memory`, `create_careops_task`). Note the success state and latency.
- Explain the **MongoDB Activity** panel (number of collections touched and overall write counts), confirming the system is using real persistence.

**Step 7: Task Lifecycle & Human-in-the-loop**
- Look at the newly generated proposed tasks in the **Task Board**.
- Show that they default to `proposed` and have a yellow badge.
- Click **Approve** on a task to transition it to `approved`, proving the Human-in-the-Loop requirement.
- Click **Start Work** and **Mark Done** to show the full lifecycle.

**Step 8: Safety Verifier Blocking (Unsafe Example)**
- Update the synthetic note input to include clinical directions (e.g. "Diagnose with migraine and prescribe 50mg of Advil").
- Hit **Run CareOps Agent**.
- Show the Run Status panel flagging "Excluded Items: 1 (Clinical decisions blocked)".
- Show the **Controlled MongoDB Tools** panel marking `create_careops_task` as `blocked` with a red error due to the unsafe clinical terms.

## Timing
The full demo can be executed comfortably in under 3 minutes, hitting all major hackathon judging points (Persistence, Prompting/Structured Output, Tools, Safety, Architecture).
