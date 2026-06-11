# Phase 5B.5d — Run Explanation Panel / Demo Story Layer

## 1. Phase Name and Purpose
**Phase:** Phase 5B.5d — Run Explanation Panel / Demo Story Layer
**Purpose:** To make the product value and technical evidence immediately visible in the UI by adding a clear, plain-language “What happened in this run?” panel after a run completes. This layer explicitly clarifies the agent's function, constraints, and safety boundaries for demonstration purposes.

## 2. Deployed State
* **Project:** MyuKura CareOps Memory Agent
* **API Image:** smoke-v11
* **API Revision:** myukura-careops-api-00014-4ps
* **API URL:** https://myukura-careops-api-1001238764138.europe-west1.run.app
* **Web Image:** smoke-web-v7
* **Web Revision:** myukura-careops-web-00007-ldb
* **Web URL:** https://myukura-careops-web-1001238764138.europe-west1.run.app
* **Backend:** MongoDB Atlas
* **state_backend:** mongodb
* **Mode:** Mock deterministic extraction
* **Data:** Synthetic data only

## 3. What Changed in the UI
* Added a “What happened in this run?” panel directly below the Operational Memory Created block.
* Extracted and displayed actual data points (signal count, current task count, collections touched).
* Included conditional rendering for scenario-specific safe explanations based on detected signals.
* Ensured the panel uses strictly safe, operational vocabulary.

## 4. What the Panel Explains
The panel contains five core explanation blocks:
1. **Source note understood:** Clarifies the note is treated as administrative context, not a diagnostic source.
2. **Operational signals detected:** Explains the identification of operational indicators (and shows the count).
3. **Tasks proposed:** Explains that tasks are non-clinical, pending human approval, and linked to source evidence.
4. **Memory persisted:** Confirms that the note, run, tasks, and audit logs are written to MongoDB.
5. **Safety boundary applied:** Explicitly states the agent did not diagnose, recommend treatment, change medication, or contact the patient.

## 5. Scenario 1 Validation Summary
*(Messy post-visit admin note — forms, insurance and follow-up)*
* “What happened in this run?” panel appears successfully.
* **Signals detected:** 9
* **Tasks proposed:** 7
* **MongoDB Backend:** Active (Collections touched: 8).
* **Safety boundary:** Visible.
* **Scenario-specific notes visible:**
  * Insurance verification
  * Form/consent uncertainty
  * Communication restriction
* Current Run and Memory Total are cleanly separated.
* Source evidence is visible per task.
* **Result:** No white screen, full success.

## 6. Scenario 4 Validation Summary
*(Mixed-patient admin cleanup — must be flagged)*
* “What happened in this run?” panel appears successfully.
* **Signals detected:** 6
* **Tasks proposed:** 4
* **Scenario-specific notes visible:** Mixed-patient warning.
* Task “Flag mixed-patient note for human review” visible.
* **MongoDB Backend:** Active.
* Current Run and Memory Total are cleanly separated.
* Source evidence is visible per task.
* **Result:** No white screen, full success.

## 7. MongoDB Evidence
* **Writes Increase:** The panel and audit timeline reflect database activity correctly.
* **Collections Touched:** Up to 8 collections modified per run.
* **Active Collections:** 
  * `source_notes`
  * `agent_runs`
  * `careops_tasks`
  * `agent_audit_logs`
  * `task_status_history`

## 8. Safety Boundaries
* **No diagnosis** created.
* **No treatment recommendations** made.
* **No medication changes** enacted.
* **No real external delivery** (no messages sent or actual appointments booked).
* **Human approval required** for all proposed tasks.
* **Synthetic demo only:** No real patient data used.

## 9. Gemini Status
* **Disabled:** Currently completely disabled in this stable demo path.
* **Mode:** Utilizing Mock deterministic extraction only.
* **Future:** Gemini can be added later as an optional extraction layer without breaking the established mock demo path.

## 10. Known Limitations
* Mock mode is strictly rule-based, not utilizing true LLM reasoning.
* No MCP tool calls occur in mock mode yet.
* The Persisted Tasks list is currently long and unpaginated/unfiltered; it requires cleanup.
* No Voice Intake exists yet.
* No Visual/Admin Note Intake exists yet.
* No real external connectors are hooked up.

## 11. Next Recommended Phase
1. **Phase 5B.5e** — Persisted Memory Display Cleanup
2. **Phase 5B.6** — Voice Intake
