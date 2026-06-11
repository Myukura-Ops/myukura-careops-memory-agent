# Final Demo Video Script

This document contains modular scripts for recording the Devpost demo video, ensuring strict adherence to the project's safety boundaries and partner integration limits. 

**IMPORTANT RECORDING RULES:**
*   Do NOT show the secret access code (`DEMO_ACCESS_CODE`) on screen or say it aloud. Ensure the UI is already unlocked or the password field is obfuscated when recording.
*   Do NOT claim that Arize or Elastic external exports are live. Use the exact wording provided.
*   Do NOT claim the agent performs clinical diagnosis, treatment planning, or medication changes. Emphasize "CareOps" and "Administrative Tasks".
*   Emphasize that the demo uses ONLY synthetic data.

---

## 2-Minute Script (Lightning Pitch)

**[0:00 - 0:30] Introduction & Problem**
"Hi, we're building the MyuKura CareOps Memory Agent. In modern clinics, after a patient visit, critical operational tasks—like follow-ups, insurance verification, and scheduling—often fall through the cracks because they are buried in unstructured notes. Our agent solves this by automatically extracting these CareOps tasks."

**[0:30 - 1:00] The Solution & Safety (Screen: Access Gate & Empty UI)**
"Security and safety are our top priorities. The public demo is protected by a backend-enforced access code, and we strictly enforce a 6,000-character text limit and a 5-minute voice limit to prevent abuse. Furthermore, this agent strictly refuses clinical decision-making, focusing entirely on administrative operations with synthetic data."

**[1:00 - 1:30] Gemini & Memory in Action (Screen: Running Gemini with a note)**
"Let's see it in action. We input a synthetic post-visit note. Using Google Gemini 1.5 Flash, the agent parses the unstructured text and extracts structured operational tasks. But it doesn't just process this visit in isolation. Powered by MongoDB Atlas as our live persistent operational memory, the agent retrieves past operational context to enrich the current tasks."

**[1:30 - 2:00] Partner Architecture & Conclusion (Screen: Partner & Evidence Panels)**
"To ensure enterprise readiness without risking public data leaks, we built an outbox-ready architecture. Our Arize observability layer and Elastic audit-search layer are fully integrated to generate payloads, but external export is safely disabled for this public demo. The MyuKura CareOps Agent: closing the loop on patient care operations safely and efficiently."

---

## 3-Minute Script (Standard Devpost)

**[0:00 - 0:40] Introduction, Problem & Access Control**
"Welcome to the MyuKura CareOps Memory Agent demo. Clinical staff lose hours deciphering unstructured post-visit notes to extract actionable administrative tasks—like scheduling follow-ups or verifying insurance. We built an AI agent to automate this. Because we are dealing with healthcare operations, security is paramount. Our live demo is protected by a backend access gate, and we enforce strict limits: a 6,000-character max for notes and 5-minutes for voice ingestion."

**[0:40 - 1:20] Prompt Injection & AI Safety (Screen: Triggering a prompt injection)**
"Before we show a successful run, let's talk about safety. If an adversarial user tries a prompt injection or asks for a clinical diagnosis, our dual-layer safety validator immediately intercepts and rejects the request. Human review is always required, and the agent refuses to practice medicine."

**[1:20 - 2:10] The Core Flow & MongoDB Memory (Screen: Successful Gemini run)**
"Now, let's run a valid synthetic note. Powered by Google Cloud Run and Gemini 1.5 Flash, the agent extracts structured operational tasks instantly. The real magic is our state backend: MongoDB Atlas acts as our live persistent operational memory. When this patient returns, the agent queries MongoDB to retrieve past operational context—like a previous language preference or an unresolved billing issue—and injects it directly into the Gemini prompt."

**[2:10 - 3:00] Partner Architecture & Evidence (Screen: Partner Integration Panels)**
"Enterprise healthcare requires deep observability and auditability. We've architected an outbox pattern for our partners. The system continuously generates payloads for the Arize observability layer and the Elastic audit-search layer. To protect data in this public hackathon environment, external export and indexing are safely disabled, but the outbox logic is fully operational. Thank you for watching!"

---

## 5-Minute Script (Deep Dive)

**[0:00 - 1:00] The CareOps Crisis**
*(Expand on the 3-minute intro. Talk about the burden on administrative staff, the cost of dropped follow-ups, and the strict distinction between clinical care and CareOps.)*

**[1:00 - 2:00] Security, Safety & Boundaries**
*(Show the access code screen, demonstrate the 6,000-character limit rejecting a large note, and demonstrate the prompt injection defense. Emphasize that all data is synthetic.)*

**[2:00 - 3:30] Gemini Extraction & Persistent Memory**
*(Run a note. Walk through the extracted tasks in the UI. Then, run a SECOND note for the same synthetic patient. Highlight the "Existing Memory Found" panel. Explain how MongoDB Atlas stores the tasks, and how the agent queries them to build a temporal context window for Gemini.)*

**[3:30 - 4:30] The Outbox Pattern & Partner Integrations**
*(Scroll down to the Partner Integrations panel. Explain the `PartnerOutbox` MongoDB collection. Explain why Arize and Elastic are outbox-ready rather than directly exporting data (security, compliance, avoiding synchronous failure points in the critical path).)*

**[4:30 - 5:00] Deployment Evidence & Conclusion**
*(Show the Evidence Layer at the bottom. Point out the Cloud Run deployment and the transparency of the architecture. Conclude with the vision of the product.)*
