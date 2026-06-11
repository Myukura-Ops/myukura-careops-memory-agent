# Demo Script

## 2-Minute Version
**The Problem:** Small and medium clinics lose massive amounts of operational context after visits. Forms, insurance, language preferences, and incomplete handoffs easily slip through the cracks.
**Live Note:** We use our secure Voice Intake component or text interface to record a natural, messy clinical interaction.
**Gemini Extraction:** We click "Gemini Safe Extraction." Gemini structures the operational signals automatically.
**Memory Reuse:** In this example, the patient returns. Notice how Gemini automatically remembers their previous language preference natively from our MongoDB Atlas datastore.
**Safety Validator:** We enforce absolute boundaries. No diagnosis, no medication changes—the system requires human approval for everything.
**Google Architecture:** This runs securely on Cloud Run using Secret Manager and MongoDB.
**Closing Line:** "MyuKura CareOps Memory Agent: supervised, safe, and context-aware clinic operations built on Google Cloud."

## 5-Minute Version
**Introduction (1 min):** Walk through the problem. Clinic operations are chaotic. Show the architectural diagram highlighting React, FastAPI, Gemini, and MongoDB on Google Cloud Run.
**Voice Intake (1 min):** Dictate a messy note directly into the system using the integrated Voice Intake tool to simulate a doctor walking between rooms.
**Safe Extraction & Memory (1.5 mins):** Execute the run. Point out the Evidence Layer showing the `gemini-3.5-flash` model used. Focus on the "Existing Memory" panel. Explain how MongoDB dynamically injected previous patient context directly into the prompt securely.
**Prompt-Injection Defense (1 min):** Switch the note to a malicious injection attempt requesting the system prompt and a medication change. Run it. Show how the backend safety validator intercepts it and flags it as "Failed Validator." The system strips the unsafe instructions and defaults safely to human review.
**Audit Timeline & Evidence Layer (0.5 mins):** Emphasize transparency. Show the audit timeline and the explicit read-out of the AI's fallback states and model versions. Close by reinforcing the boundary rules: "Supervised AI for administrative scaling, not clinical risk."
