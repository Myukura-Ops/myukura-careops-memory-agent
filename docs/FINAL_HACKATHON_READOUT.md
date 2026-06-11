# MyuKura CareOps Memory Agent

**One-sentence product statement:**
MyuKura CareOps Memory Agent is a supervised clinic operations memory agent that turns messy post-visit operational notes into safe, auditable, human-reviewed tasks using Gemini, MongoDB memory, and Google Cloud.

## The Problem
Small and medium clinics lose operational context after visits: forms, insurance, follow-ups, language preferences, and incomplete handoffs easily slip through the cracks.

## Our Solution
Gemini securely extracts operational signals from post-visit notes; a backend safety validator enforces rigid medical boundaries; MongoDB actively stores operational memory. Future agent runs natively reuse this memory to identify missed context. Humans approve all tasks—providing a supervised AI ops system.

## Architecture
- **Frontend:** React Web App + Vite + Tailwind CSS
- **Backend:** FastAPI + Python
- **Infrastructure:** Google Cloud Run (API/Web), Cloud Build, Artifact Registry
- **AI Core:** Gemini API (gemini-3.5-flash) with Model Fallback Chain
- **Security:** Secret Manager, Mock Fallback Mechanism
- **Persistence:** MongoDB Atlas with repository pattern
- **Partner Integrations:**
  - MongoDB is live.
  - Arize/Elastic outbox payloads are generated.
  - Partner worker dry-run processes pending outbox items when external export is disabled.
  - External Arize/Elastic exports are not activated in this demo unless explicitly configured.
  - The core CareOps run is independent from partner availability.
- **Observability:** Audit logs

## Safety Features
- Operates on synthetic demo data only
- **Hard Boundaries:** No diagnosis, no treatment recommendations, no medication changes, no real external delivery
- **Prompt-Injection Defense:** Detects and safely strips malicious instructions
- **Supervision:** Human approval required for all generated tasks
- *Note:* No HIPAA/GDPR production compliance claims are made for this prototype.

## Demo Flow
1. **Safe Extraction:** Translates messy natural language notes into distinct administrative tasks.
2. **Memory Reuse:** Recognizes returning patients and injects known operational context directly into Gemini.
3. **Prompt-Injection Defense:** Rejects adversarial instructions while maintaining clinical operations.
4. **Voice Intake:** Seamless HTTPS dictation input for busy professionals.
5. **Evidence Layer:** Transparently exposes `model_used`, `fallback_status`, `safety_status`, and `memory_found` context to users.

## Evidence Snapshot
- **API Health:** `healthy` (Gemini enabled natively)
- **Deployed Revisions:** `myukura-careops-api-00016-pdz`, `myukura-careops-web-00008-b6t`
- **Gemini Extraction Run ID:** `b33171fe-b46b-42b2-9306-c1c3f2314365`
- **Prompt-Injection Run ID:** `dd76e6c6-ef59-45c5-b513-c50329673228`
- **MongoDB Memory:** Integrated natively with dynamic injection into prompts.

## Current Limitations
- No real authentication/tenant access control yet
- No real patient data
- No production compliance claims
- No real external delivery
- Confined to local/demo scope
- Model output still requires validation and human review
