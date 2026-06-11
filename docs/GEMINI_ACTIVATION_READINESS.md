# Gemini Activation Readiness

## 1. Current Status

* **Code Path:** The Gemini orchestration code path, fallback models configuration, safety validators, and prompt injection defense exist locally in the codebase.
* **Activation:** Gemini is **NOT** activated yet. `GEMINI_ENABLED` defaults to `false`.
* **Security:** No real API key is stored in the repository. The `.env.example` file contains safe placeholders only (`GEMINI_API_KEY_NOT_CONFIGURED`).
* **Fallback:** The deterministic Mock Extraction remains the default and the absolute final fallback in the event of Gemini failures.

## 2. Local Activation Process

To test Gemini locally, follow these safe steps:

1. Obtain or create a Gemini API key outside of this repository (e.g. from Google AI Studio).
2. Export the environment variables directly in your terminal, or place them in an explicitly ignored `.env` file (`apps/api/.env`).
3. **DO NOT** paste the API key into any chat, documentation file, screenshot, commit message, or source code.

Example command (with placeholder):
```bash
export GEMINI_API_KEY=""
```

## 3. Required Local Environment Variables

To activate the real Gemini extraction locally, you must provide:

```env
GEMINI_ENABLED=true
GEMINI_API_KEY="your_real_key_here"
GEMINI_PRIMARY_MODEL="gemini-3.5-flash"
GEMINI_FALLBACK_MODELS="gemini-3.1-flash-lite,gemini-2.5-flash"
GEMINI_MAX_MODEL_ATTEMPTS=3
GEMINI_REQUEST_TIMEOUT_SECONDS=20
```

## 4. Suggested Model Chain

* **Primary:** Gemini 3.5 Flash (`gemini-3.5-flash`) if available.
* **Fallback 1:** Gemini 3.1 Flash-Lite (`gemini-3.1-flash-lite`) if available.
* **Fallback 2:** Gemini 2.5 Flash (`gemini-2.5-flash`) if available.

*Note: Exact model IDs must be verified against the current Google AI Studio / Vertex availability before running.*

## 5. Safety Boundaries

When running in Gemini mode, the following boundaries are enforced:

* **Untrusted Input:** Source notes are treated as untrusted input.
* **Prompt Injection Defense:** Active defense logic guards against overriding system rules, role changes, or clinical commands. Unsafe tasks are stripped and logged as `prompt_injection_or_unsafe_instruction_detected`.
* **Backend Validator:** Strips unsafe clinical tasks before they can be persisted.
* **Enforced Restrictions:**
  * No diagnosis.
  * No treatment recommendations.
  * No medication changes.
  * No external delivery.
  * Human approval is strictly required for all proposed operational tasks.

## 6. Cloud Activation Later

* **DO NOT** enable Cloud Run Gemini environment variables until the local smoke test passes successfully.
* **DO NOT** create a Secret Manager secret for the API key until the local smoke test passes, unless explicitly approved by the Architect.
* Any Cloud activation must be treated as a separate, Architect-approved phase.
