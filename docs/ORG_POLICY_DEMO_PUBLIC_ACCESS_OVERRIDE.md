# Organization Policy Demo Public Access Override

**Date:** 2026-06-08

## Summary
To enable public access for the Cloud Run API during the hackathon demo, a project-level Organization Policy override was applied. This bypasses the inherited "Domain Restricted Sharing" constraint that otherwise blocked assigning the `allUsers` role.

## Project Details
- **Project ID:** `myukura-careops-demo`
- **Project Number:** `1001238764138`
- **Organization ID:** `620044798702`

## Policy Details
- **Original Blocker:** Domain Restricted Sharing. Only members from the allowed customer/domain `C0449wm7d` were permitted. This blocked adding `allUsers`.
- **Exact Policy Constraint:** `constraints/iam.allowedPolicyMemberDomains`
- **Override Applied:** `projects/1001238764138/policies/iam.allowedPolicyMemberDomains`

**Policy Content:**
```yaml
spec:
  rules:
  - allowAll: true
```

## Rationale & Scope
- **Why it was needed:** To allow unauthenticated public invocation (`roles/run.invoker`) of the `myukura-careops-api` Cloud Run service strictly for the temporary hackathon demo.
- **What it exposes:** It exposes only the Cloud Run services in this specific project to the public internet. It does NOT expose other projects or alter the organization-wide policy.
- **Public URL now working:** `https://myukura-careops-api-1001238764138.europe-west1.run.app/health`

## Safety Constraints
**IMPORTANT:** This is NOT production security. This is a temporary hackathon demo exception.
- The project uses **synthetic demo data only**.
- No real PHI/PII.
- No real patient data.
- No real delivery.
- No diagnosis, treatment, or medication automation.
- Secrets remain protected.
- MongoDB is not connected yet.
- Gemini is disabled.
- Frontend is not deployed yet.

## Verification Command & Result
```bash
curl -s https://myukura-careops-api-1001238764138.europe-west1.run.app/health
```

**Result:**
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

## Rollback & Revert Instructions

When the hackathon is complete, this override must be removed.

**1. Remove allUsers from Cloud Run:**
```bash
gcloud beta run services remove-iam-policy-binding myukura-careops-api \
  --project=myukura-careops-demo \
  --region=europe-west1 \
  --member=allUsers \
  --role=roles/run.invoker
```

**2. Delete the project-level org policy override (returns to inherited org policy):**
```bash
gcloud org-policies delete constraints/iam.allowedPolicyMemberDomains \
  --project=myukura-careops-demo
```

**3. Verify restoration of the policy:**
```bash
gcloud org-policies describe constraints/iam.allowedPolicyMemberDomains \
  --project=myukura-careops-demo \
  --effective \
  --format=yaml
```
