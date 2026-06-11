# Phase 5B Pre-Deploy Checklist

## 1. Google Cloud Project Prep
- [x] Ensure the correct Google Cloud Project is selected.
  - **Confirmed Project ID**: `myukura-careops-demo`
- [x] Confirm Billing is actively enabled.
- [x] Confirm the deployment region will be `europe-west1`.

## 2. API Enablement (To be run later)
- [x] `run.googleapis.com`
- [x] `artifactregistry.googleapis.com`
- [x] `cloudbuild.googleapis.com`
- [x] `secretmanager.googleapis.com`
- [x] `iam.googleapis.com`
- [x] `logging.googleapis.com`

## 3. Org Policy & Network Access
- [x] Organization Policy override applied for demo public access
- [x] Cloud Run API public /health verified
- [ ] Must be reviewed/reverted after hackathon

## 4. Storage & Secrets Planning
- [x] **Artifact Registry**: Repo `myukura-careops-repo` successfully created in `europe-west1`.
- [ ] **Secret Manager**:
  - `MYUKURA_MONGODB_URI` (Pending local env vars)
  - `MYUKURA_GEMINI_API_KEY` (Pending local env vars)
  - *Note: These will be set from the local terminal. Gemini key stays local only.*
- [ ] **MongoDB Atlas**:
  - Note that the temporary `0.0.0.0/0` IP allowlist will be used for the initial hackathon deployment. This must be restricted afterward.
  - Action Required: Ensure cluster exists, user exists, DB is `myukura_careops_demo`, and network access is properly configured.
- [x] **Sensitive Data Guardrails**:
  - Synthetic demo seed only (no real data).
  - Logging/tracing redaction confirmed.
  - Sensitive-data guardrails documented.
  - No compliance claims (HIPAA/GDPR).

## 4. Code & Build Readiness
- [x] **Dockerfiles**: Both `apps/api/Dockerfile` and `apps/web/Dockerfile` are present and optimized for Cloud Run.
  - API uses dynamic `$PORT`.
  - Web uses multi-stage Nginx substituting `$PORT`.
- [x] **Health Check**: `/health` endpoint is safe and does not leak secrets.
- [ ] **CORS Strategy**: 
  - Deploy API first to get URL.
  - Build Web injecting `VITE_API_BASE_URL`.
  - Deploy Web to get URL.
  - Update API `CORS_ALLOWED_ORIGINS` with exact Web URL.

## Status
**NO DEPLOY YET.** We are currently pending project ID confirmation to proceed with infrastructure creation.
