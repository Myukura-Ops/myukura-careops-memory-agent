# Safety and Compliance

The MyuKura CareOps Memory Agent is designed strictly as a demonstration of an operational memory agent. It is explicitly NOT a clinical decision support system or a medical device.

## Core Principles
- **Synthetic Data Only**: All testing, demonstration, and deployment will use synthetic demo data only.
- **No Real Patient Data**: The application will not connect to live EHRs or process real patient PHI/PII.
- **No Diagnosis**: The agent will not perform medical diagnosis.
- **No Treatment Recommendations**: The agent will not recommend treatments.
- **No Medication Changes**: The agent will not suggest or enact changes to medication.
- **Human-in-the-Loop**: The system is designed to generate draft operational tasks and handoffs that must be approved by a human user before simulated action.
- **Simulated Delivery**: Integrations like WhatsApp or email are simulated for the MVP.
- **Audit Logging**: All agent actions are durably logged to MongoDB for traceability.

## Input Limits
Input texts to the agent will be size-limited and sanitized to ensure stability and reduce risks of injection.
