# MyuKura CareOps Demo: Org Policy Exception Guide

## 1. Current Diagnosis
- **Project:** `myukura-careops-demo`
- **Organization:** `620044798702`
- **API Status:** Cloud Run API (`myukura-careops-api`) is deployed and 100% healthy. It responds successfully to authenticated requests.
- **Ingress:** Cloud Run ingress is configured to `allowAll`.
- **Blocker:** `allUsers` IAM binding is explicitly blocked by the organization policy constraint `constraints/iam.allowedPolicyMemberDomains`.
- **Diagnosis:** This is Domain Restricted Sharing. It enforces that only members from the specific Google Workspace Customer ID can be granted IAM roles.

## 2. Goal
Allow unauthenticated public invocation for the demo Cloud Run service. Ideally, this exception should be scoped ONLY for:
- The project `myukura-careops-demo`
- The service `myukura-careops-api`
- The duration of the temporary hackathon demo

## 3. Manual Admin Options

### Option A: Project-Level Exception (Recommended)
Create a project-level exception to the Domain Restricted Sharing policy (`constraints/iam.allowedPolicyMemberDomains`) specifically for `myukura-careops-demo`. This allows `allUsers` to be added to the Cloud Run invoker role without affecting the rest of the organization.

### Option B: Temporarily Relax Policy
Temporarily relax `allowedPolicyMemberDomains` only for this project, and not the whole organization, during the hackathon period.

### Option C: External Public Demo Project
If a project-level exception is not possible or takes too long, create a separate public demo project entirely outside of this restrictive organization.

## 4. Safety Constraints
Please keep the following constraints in mind for this demo environment:
- **Synthetic demo data only.**
- **No real PHI/PII.**
- **No real delivery.**
- **No diagnosis, treatment, or medication automation.**
- A demo access code should be added later at the application layer if public access is granted.
- Public access must be removed or the restrictive policy restored immediately after the hackathon if required.

## 5. Commands for AFTER Admin Exception ONLY
*(Do NOT run these commands until the Org Admin has granted the exception)*

```bash
gcloud beta run services add-iam-policy-binding myukura-careops-api \
  --region=europe-west1 \
  --member=allUsers \
  --role=roles/run.invoker
```

## 6. Verification After Exception
Once the IAM policy is applied, verify unauthenticated access with:

```bash
curl -s https://myukura-careops-api-1001238764138.europe-west1.run.app/health
```

**Expected JSON response:**
```json
{
  "status": "healthy",
  "app_env": "demo",
  "runtime": "cloud_run",
  "state_backend": "memory",
  "demo_mode": true,
  "gemini_enabled": false,
  "observability_enabled": false,
  "mongodb_status": "not_checked"
}
```

## 7. Fallback Plan
If an organization exception is not feasible within a reasonable time frame:
1. Create an external, public demo GCP project outside the organization.
2. Redeploy the exact same API image and architecture to the new project.
3. Keep MongoDB Atlas external.
4. Keep all sensitive-data guardrails intact.
