# Final Screenshot Plan

This document outlines the required screenshots for the Devpost submission to clearly communicate the value, safety, and functionality of the MyuKura CareOps Memory Agent.

**IMPORTANT:** Do NOT include the live demo access code in any screenshot. Mask it or capture after the UI is unlocked.

## 1. Access-code gate
*   **What to capture:** The initial UI screen showing the secure access code lock, before the application is usable.
*   **Why it matters to judges:** Demonstrates immediate security, quota protection, and safety boundaries for a live public demo.
*   **Suggested caption:** "Secure Access Gate: Protecting public endpoints and Google Cloud quotas while allowing reviewers to evaluate the system safely."

## 2. Main demo UI after unlock
*   **What to capture:** The clean, unlocked main interface showing the patient intake form and the right-side control panels.
*   **Why it matters to judges:** Shows the user experience, professional design, and clear operational focus.
*   **Suggested caption:** "CareOps Workspace: A clean interface designed for clinical administrative staff to process post-visit notes."

## 3. Source note input with 6,000-char counter
*   **What to capture:** The source note text area filled with text, highlighting the `X / 6000` character counter at the bottom.
*   **Why it matters to judges:** Proves that strict input safety boundaries and limitations have been proactively designed and enforced in the UI.
*   **Suggested caption:** "Input Boundaries: Strict character limits ensure the agent only processes bounded, appropriate operational notes."

## 4. Voice intake section with 5-minute safety note
*   **What to capture:** The voice recording component displaying the "Maximum 5-minute recording" safety disclaimer.
*   **Why it matters to judges:** Demonstrates human-centric design with clear expectations and safe boundaries for voice ingestion.
*   **Suggested caption:** "Voice Intake Limits: Clear constraints on audio recordings to prevent abuse and enforce synthetic demo boundaries."

## 5. Successful Gemini run result
*   **What to capture:** The generated tasks and audit events in the right panel after a successful Gemini extraction.
*   **Why it matters to judges:** Showcases the core value proposition: converting unstructured notes into structured, operational CareOps tasks.
*   **Suggested caption:** "Operational Memory Extracted: Gemini 1.5 Flash instantly parses the note and queues actionable tasks for human review."

## 6. Gemini Model Attempts panel
*   **What to capture:** The detailed breakdown of the model execution chain (e.g., Gemini 3.5 Flash primary attempt).
*   **Why it matters to judges:** Highlights transparency, multi-model fallback capability, and the robust orchestrator design.
*   **Suggested caption:** "Execution Transparency: Detailed trace of Gemini model attempts and fallback paths for high reliability."

## 7. Existing Memory panel
*   **What to capture:** The "Existing Memory Found" panel displaying prior injected tasks during a subsequent run.
*   **Why it matters to judges:** Proves the system possesses persistent operational memory that carries context across isolated visits.
*   **Suggested caption:** "Persistent Context: The agent retrieves previous operational tasks from MongoDB to enrich current decision-making."

## 8. Partner Integrations panel
*   **What to capture:** The partner integrations panel showing MongoDB as "Integrated" and Arize/Elastic as "Outbox ready / External export disabled".
*   **Why it matters to judges:** Validates the multi-partner integration while proving that external exports are safely disabled for the public demo.
*   **Suggested caption:** "Safe Partner Ecosystem: MongoDB operational memory is live, while Arize and Elastic are primed via an outbox pattern for future enterprise deployment."

## 9. Safety/prompt-injection result
*   **What to capture:** The UI showing a rejected run with the "Failed Safety Validation" or prompt-injection warning.
*   **Why it matters to judges:** Crucial for AI safety. Proves the system actively defends against adversarial inputs and refuses out-of-scope instructions.
*   **Suggested caption:** "AI Safety First: The agent intercepts and safely rejects prompt-injection attacks and out-of-scope clinical requests."

## 10. Evidence Layer / Deployment Status
*   **What to capture:** The bottom "Evidence Layer" and "Deployment Status" components detailing the architecture and GCP status.
*   **Why it matters to judges:** Provides technical proof of execution, verifying that the demo is running on actual Google Cloud infrastructure.
*   **Suggested caption:** "Verifiable Architecture: Transparent proof of our Google Cloud Run deployment, MongoDB Atlas integration, and system safety boundaries."
