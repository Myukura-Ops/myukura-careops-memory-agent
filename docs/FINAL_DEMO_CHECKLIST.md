# Final Demo Checklist

- [ ] Open Web URL (https://myukura-careops-web-1001238764138.europe-west1.run.app)
- [ ] Hard refresh to ensure latest static assets
- [ ] Confirm API health: Check `https://myukura-careops-api-1001238764138.europe-west1.run.app/health` explicitly says `gemini_enabled: true` and `status: healthy`
- [ ] Run safe Gemini note: Verify tasks generate without errors, `model_used` is visible, and it flags for human review
- [ ] Run memory reuse note: Check that the "Existing Memory" panel surfaces previous patient facts natively from MongoDB
- [ ] Run prompt-injection note: Confirm the safety validator rejects the request and strips malicious actions
- [ ] Capture screenshots of the Evidence Layer, Voice Intake, and Prompt-Injection defense blocks
- [ ] Confirm no real patient data is used (synthetic demo only)
- [ ] Confirm MongoDB memory indicators reflect active persistence
- [ ] Confirm fallback to Mock mode is still available via the dropdown selection
- [ ] Confirm all safety and "human review" disclaimers are visible on screen
- [ ] Confirm no overclaims regarding HIPAA/GDPR are present on the interface
