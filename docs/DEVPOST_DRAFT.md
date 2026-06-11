# Devpost Draft: MyuKura CareOps Memory Agent

## 1. Project Title
MyuKura CareOps Memory Agent

## 2. One-Liner
A secure, memory-augmented AI agent that extracts operational and administrative tasks from post-visit clinical notes.

## 3. Inspiration
In modern healthcare, clinical visits generate a massive amount of unstructured data. While doctors focus on clinical care, the administrative and operational tasks—scheduling follow-ups, verifying insurance, organizing referrals—often fall through the cracks. These dropped "CareOps" tasks lead to poor patient experiences and lost clinic revenue. We realized that AI shouldn't just be used for medical diagnosis; it's desperately needed for safe, efficient administrative operations.

## 4. What it does
The MyuKura CareOps Memory Agent acts as a secure, automated administrative assistant. It ingests synthetic post-visit notes (via text or voice) and uses Google Gemini 1.5 Flash to extract structured operational tasks. Crucially, the agent possesses persistent operational memory. When a returning patient's note is processed, the agent queries MongoDB Atlas for past operational context (e.g., language preferences, pending billing issues) and injects it into the AI's prompt, ensuring continuity of care operations across isolated visits.

## 5. How we built it
We built a decoupled architecture on Google Cloud. The frontend is a React application served via Cloud Run. The backend is a FastAPI Python service, also deployed on Cloud Run, which orchestrates the AI logic. We integrated Google Secret Manager to securely handle API keys and access codes. To handle the AI processing, we utilized Google's `google-genai` SDK to interface with Gemini 1.5 Flash.

## 6. Partner Technologies Used
*   **Google Cloud:** Cloud Run, Secret Manager, Gemini API
*   **MongoDB:** Live persistent operational memory
*   **Arize:** AI Observability (Outbox integrated)
*   **Elastic:** Audit Search (Outbox integrated)

## 7. Google Cloud Architecture
Our system relies entirely on Google Cloud infrastructure. The React web app and FastAPI backend are containerized and deployed to Cloud Run in `europe-west1`. We strictly enforce security by keeping our Gemini API keys and Demo Access Codes locked inside Google Cloud Secret Manager, ensuring our Cloud Run service accounts only access what they need.

## 8. MongoDB Architecture
MongoDB Atlas serves as the backbone of our agent's state. It provides **live persistent operational memory**. We store all agent runs, extracted tasks, and source notes in MongoDB. Before Gemini processes a new note, our repository layer queries MongoDB for the patient's recent operational tasks, building a temporal context window that allows the AI to "remember" past administrative requirements.

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
In the future, we plan to fully enable the Arize and Elastic outbox workers for real-time external observability. We also aim to expand the agent's capabilities to integrate directly with EHR systems via FHIR APIs, moving from proposing tasks to actively assisting in their completion.

## 15. Demo Instructions
Our live demo is publicly accessible but protected by an access gate.
URL: `[INSERT_LIVE_URL]`
*Reviewers: Please refer to your submission materials or contact us for the secure `DEMO_ACCESS_CODE`.*

## 16. Security/Privacy Note
The public web shell is reachable, but costly and mutating API actions are protected by a backend-enforced demo access code. 

## 17. Limitations
This is a synthetic demonstration only. It contains no real patient data. The system does not provide medical advice. Advanced features like OCR, PDF parsing, and handwritten analysis are not active in this demo.
