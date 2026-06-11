# Devpost Draft: MyuKura CareOps Memory Agent

## 1. Project Title
MyuKura CareOps Memory Agent

## 2. One-Liner
A secure, memory-augmented AI agent that extracts operational and administrative tasks from post-visit clinical notes.

## 3. Inspiration
In modern healthcare, clinical visits generate a massive amount of unstructured data. While doctors focus on clinical care, the administrative and operational tasks—scheduling follow-ups, verifying insurance, organizing referrals—often fall through the cracks. These dropped "CareOps" tasks lead to poor patient experiences and lost clinic revenue. We realized that AI shouldn't just be used for medical diagnosis; it's desperately needed for safe, efficient administrative operations.

## 4. What it does
The MyuKura CareOps Memory Agent acts as a secure, automated administrative assistant. It ingests synthetic post-visit notes (via text or voice) and uses Google Gemini (gemini-3.5-flash with an automatic fallback chain) to extract structured operational tasks. Crucially, the agent possesses persistent operational memory. When a returning patient's note is processed, the agent reads past operational context (e.g., language preferences, pending billing issues) from MongoDB Atlas **through the official MongoDB MCP Server (read-only)** and injects it into the AI's prompt, ensuring continuity of care operations across isolated visits.

## 5. How we built it
We built a decoupled architecture on Google Cloud. The frontend is a React application served via Cloud Run. The backend is a FastAPI Python service, also deployed on Cloud Run, which orchestrates the AI logic. We integrated Google Secret Manager to securely handle API keys and access codes. AI processing uses Google's `google-genai` SDK with a resilient model chain (gemini-3.5-flash primary, automatic fallbacks, every attempt surfaced in the UI). Operational memory reads run through the official MongoDB MCP Server, spawned over stdio in read-only mode inside the API container, with an audited fallback to our controlled native adapter.

**A deliberate architecture decision:** we did not orchestrate the agent through a high-level agent framework. In a healthcare context, autonomous black-box agent loops were unacceptable to us. We built a deterministic orchestrator directly on the Gemini SDK so that **every single model output must pass through our dual-layer safety validator and be written to the audit trail before any task can even be proposed**. Maximum clinical-safety control was worth more to us than framework convenience — and it is the reason we can show a complete, replayable audit timeline for every run.

## 6. Partner Technologies Used
*   **Google Cloud:** Cloud Run, Cloud Build, Artifact Registry, Secret Manager, Gemini API
*   **MongoDB (our partner track):** Official MongoDB MCP Server (read-only memory reads) + MongoDB Atlas as live persistent operational memory, task storage and audit trail
*   **Arize (roadmap):** AI observability layer — outbox pattern with an implemented export worker, external export disabled in the public demo
*   **Elastic (roadmap):** Audit-search layer — outbox pattern with an implemented indexing worker, external indexing disabled in the public demo

## 7. Google Cloud Architecture
Our system relies entirely on Google Cloud infrastructure. The React web app and FastAPI backend are containerized and deployed to Cloud Run in `europe-west1`. We strictly enforce security by keeping our Gemini API keys and Demo Access Codes locked inside Google Cloud Secret Manager, ensuring our Cloud Run service accounts only access what they need.

## 8. MongoDB Architecture
MongoDB Atlas serves as the backbone of our agent's state. It provides **live persistent operational memory**. We store all agent runs, extracted tasks, source notes, partner outbox items and audit logs in MongoDB. Before Gemini processes a new note, the agent reads the patient's recent operational tasks and facts **through the official MongoDB MCP Server** — spawned over stdio with `--readOnly` enforced — building a temporal context window that allows the AI to "remember" past administrative requirements. Writes go through a controlled tool adapter with strict scoping and full per-call audit logging; if the MCP server is ever unavailable, the agent falls back to the native adapter and records the fallback in the audit timeline.

## 9. Arize/Elastic Partner Layer
Enterprise healthcare requires deep observability. However, synchronous third-party API calls in the critical path can cause failures. We designed a robust "Partner Outbox" pattern in MongoDB. 
*   **Arize:** An outbox-ready AI observability/evaluation layer. External export is disabled in the public demo unless explicitly configured.
*   **Elastic:** An outbox-ready audit-search layer. External indexing is disabled in the public demo unless explicitly configured.

## 10. Safety and Human-in-the-Loop
Healthcare AI must be inherently safe. 
*   **Strict Boundaries:** The agent explicitly refuses to provide clinical diagnoses, treatment plans, or medication changes. It focuses solely on CareOps.
*   **Prompt-Injection Defense:** A dual-layer safety validator intercepts adversarial instructions before they reach the main extraction logic.
*   **Input Limits:** We enforce a hard 6,000-character limit on text notes and a 5-minute limit on voice recordings to prevent abuse and enforce demo boundaries.
*   **Human-in-the-Loop:** The agent only *proposes* administrative tasks; human confirmation is always required.

## 11. Challenges
One of the biggest challenges was ensuring the system remained performant and reliable while generating payloads for multiple observability partners (Arize and Elastic). We solved this by implementing an asynchronous Outbox pattern using MongoDB, completely decoupling the partner payloads from the critical path of the user request.

## 12. Accomplishments
We successfully proved that AI can safely automate administrative healthcare operations without crossing the boundary into clinical decision-making. We are incredibly proud of our secure, persistent memory implementation that allows the agent to carry operational context across multiple patient visits.

## 13. What we learned
We learned the critical importance of AI safety guardrails and input sanitization. We also learned how to leverage Google Secret Manager effectively within a Cloud Run environment to ensure our public demo remained secure from unauthorized API usage.

## 14. What is next
The Arize and Elastic export workers are implemented and tested; next we plan to connect them to live Arize and Elastic Cloud instances for real-time external observability. We also aim to expand the agent's capabilities to integrate directly with EHR systems via FHIR APIs, moving from proposing tasks to actively assisting in their completion.

## 15. Demo Instructions
Our live demo is publicly accessible but protected by an access gate.
URL: `https://myukura-careops-web-1001238764138.europe-west1.run.app/`
*Reviewers: Please refer to your submission materials or contact us for the secure `DEMO_ACCESS_CODE`.*

## 16. Security/Privacy Note
The public web shell is reachable, but costly and mutating API actions are protected by a backend-enforced demo access code. 

## 17. Limitations
This is a synthetic demonstration only. It contains no real patient data. The system does not provide medical advice. Advanced features like OCR, PDF parsing, and handwritten analysis are not active in this demo.
