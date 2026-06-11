# Cloud Sensitive Data Guardrails

This document outlines the sensitive-data-ready architecture designed for the MyuKura CareOps Memory Agent. While the hackathon demo strictly utilizes synthetic data, the architecture is prepared for controlled production hardening, prioritizing secure secret management, redacted telemetry, and strictly scoped database access.

## A. Demo Data Policy
- **Synthetic Data Only**: The system operates exclusively on synthetic demo demographic and clinical data (`patients_demo`).
- **No Real Patient Data**: No PHI/PII is stored, processed, or logged.
- **No Real Delivery/EHR**: The application is entirely isolated; it does not connect to any real Electronic Health Record (EHR) system or deliver real messages.
- **No Clinical Automation**: The agent does not perform diagnoses, propose treatment recommendations, or make medication changes. It is strictly a supervised operational memory assistant for administrative/care operations.

## B. Secrets Policy
- **Secret Manager**: Production secrets (e.g., MongoDB URI, Gemini API Key) must be injected securely via Google Cloud Secret Manager.
- **Future Integration**: Tokens for Dynatrace or Arize Phoenix will also be managed via Secret Manager.
- **Repository Safety**: No secrets are permitted in the Git repository, Docker images, terminal prompts, application logs, or documentation.

## C. Logging Policy
- **No Full Source Notes**: Raw, full clinical note text (`source_note`) must not be printed to stdout or application logs.
- **No Raw Prompts**: Prompts containing full clinical data are not logged.
- **No Secrets**: API keys, MongoDB URIs, and authentication tokens are strictly excluded from logs.
- **Safe Metadata Only**: Logs will only output operational tracking variables: `run_id`, `status`, `error_type`, `latency`, `tool_name`, accessed `collection` names, and MongoDB document IDs (`_id`).
- **Structured Errors**: Exceptions must throw sanitized, structured error dictionaries rather than dumping raw stack traces.

## D. Observability Policy
- **Redacted Telemetry**: Traces sent to Dynatrace or Arize Phoenix must not include full clinical note text or secrets.
- **Safe Attributes Only**: Span attributes must be limited to safe metadata (e.g., latency, tool name, success/failure status).
- **Optional & Fail-Safe**: Observability hooks are strictly optional and must fail gracefully if the provider is unavailable or unconfigured. Dynatrace and Arize are evidence targets, not runtime blockers.

## E. MongoDB Policy
- **Scoped Database User**: Access to MongoDB Atlas is granted via a dedicated, strictly scoped user with least-privilege permissions.
- **Synthetic Collections**: Operations are limited to synthetic demo collections.
- **Network Access**: 
  - A temporary `0.0.0.0/0` IP allowlist will only be used for the initial rapid hackathon deployment.
  - This broad allowlist must be restricted or removed post-demo.
  - **Future Architecture**: Controlled production environments will utilize a restricted IP allowlist, static egress through Cloud NAT, or a fully private endpoint via Google Cloud Private Service Connect / VPC Peering.

## F. Sensitive Data Protection Roadmap
To further harden the system against accidental data leakage, we have documented a future integration path using **Google Cloud Sensitive Data Protection (DLP)**:
- **Pre-Persistence Inspection**: A future service endpoint (`inspect_source_note_for_sensitive_data`) could use the DLP API to inspect incoming `source_note` content before it reaches the orchestrator or MongoDB.
- **Detection Capabilities**: Identifying emails, phone numbers, standard personal identifiers, and medical record-like patterns.
- **Redaction**: The system could automatically block or redact unexpected real PHI/PII data attempting to enter the demo system.
*(Note: This is an architectural roadmap item and is not implemented in the current hackathon codebase to minimize risk).*

## G. Temporary Public Demo Exception
- **Scope:** Public Cloud Run invocation (`allUsers`) was enabled exclusively for the demo project via a temporary Organization Policy override.
- **Justification:** This is acceptable ONLY because the environment strictly uses synthetic data and no real PHI/PII is present.
- **Limitation:** This exception does NOT permit production use with real patient data. 
- **Production Standard:** Production deployments must restore the stricter organization policy (Domain Restricted Sharing) and mandate authenticated access.

## H. Compliance Statement
This demo is not certified for HIPAA/GDPR compliance. It uses synthetic data only and demonstrates a safety-oriented architecture.
