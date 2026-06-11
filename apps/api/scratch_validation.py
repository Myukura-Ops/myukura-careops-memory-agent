import sys

def mock_extract(note_content: str):
    note_content_lower = note_content.lower()
    mock_tasks = []
    signals_detected = []
    
    def get_excerpt(content: str, keywords: list) -> str:
        for kw in keywords:
            idx = content.lower().find(kw.lower())
            if idx != -1:
                start = max(0, idx - 40)
                end = min(len(content), idx + 100)
                excerpt = content[start:end].replace('\n', ' ').strip()
                return f"...{excerpt}..."
        return "not available in mock extraction."

    triggers_1 = ["follow-up", "follow up", "scheduled", "appointment", "booking", "10 days", "two weeks", "next appointment"]
    if any(k in note_content_lower for k in triggers_1):
        mock_tasks.append({
            "title": "Schedule follow-up appointment after review",
            "desc": "Create a proposed scheduling task from the source note. Do not finalize timing until the clinician or admin reviewer confirms the appropriate follow-up window.",
            "excerpt": get_excerpt(note_content, triggers_1),
            "type": "follow_up_requested"
        })
        signals_detected.append("follow_up_requested")
        
    triggers_2 = ["after clinician confirms", "exact window not confirmed", "exact day is not confirmed", "probably"]
    if any(k in note_content_lower for k in triggers_2):
        mock_tasks.append({
            "title": "Confirm follow-up timing with clinician",
            "desc": "The note mentions an approximate or unconfirmed follow-up window. Human review is required before scheduling.",
            "excerpt": get_excerpt(note_content, triggers_2),
            "type": "follow_up_needs_clinician_confirmation"
        })
        signals_detected.append("follow_up_needs_clinician_confirmation")
        
    triggers_3 = ["consent form", "intake form", "forms incomplete", "intake packet", "partially complete", "blank copy", "received"]
    if any(k in note_content_lower for k in triggers_3):
        mock_tasks.append({
            "title": "Verify intake/consent form status",
            "desc": "The note contains conflicting or incomplete form status. Check the administrative record before marking forms complete.",
            "excerpt": get_excerpt(note_content, triggers_3),
            "type": "intake_or_consent_form_uncertain"
        })
        signals_detected.append("intake_or_consent_form_uncertain")
        
    triggers_4 = ["insurance", "provider card", "new provider", "verification"]
    if any(k in note_content_lower for k in triggers_4):
        mock_tasks.append({
            "title": "Verify insurance details before next visit",
            "desc": "The note indicates insurance information may be outdated or changed. Confirm details before the next appointment.",
            "excerpt": get_excerpt(note_content, triggers_4),
            "type": "insurance_verification_needed"
        })
        signals_detected.append("insurance_verification_needed")
        
    triggers_5 = ["internal summary", "handoff", "visit summary", "chart review", "prepare the chart", "clinician review"]
    if any(k in note_content_lower for k in triggers_5):
        mock_tasks.append({
            "title": "Prepare internal summary for clinician review",
            "desc": "Prepare a non-patient-facing internal summary for clinician review. Do not send a clinical summary to the patient.",
            "excerpt": get_excerpt(note_content, triggers_5),
            "type": "internal_summary_needed"
        })
        signals_detected.append("internal_summary_needed")
        
    triggers_6 = ["portal access", "patient portal"]
    if any(k in note_content_lower for k in triggers_6):
        mock_tasks.append({
            "title": "Check patient portal access",
            "desc": "Verify portal access before sending any administrative reminder.",
            "excerpt": get_excerpt(note_content, triggers_6),
            "type": "portal_access_check_needed"
        })
        signals_detected.append("portal_access_check_needed")
        
    triggers_7 = ["emergency contact"]
    if any(k in note_content_lower for k in triggers_7):
        mock_tasks.append({
            "title": "Verify emergency contact information",
            "desc": "The note indicates emergency contact information is missing and should be completed by the front desk.",
            "excerpt": get_excerpt(note_content, triggers_7),
            "type": "emergency_contact_missing"
        })
        signals_detected.append("emergency_contact_missing")
        
    triggers_8 = ["do not send", "do not call", "call only if", "no patient-facing", "no clinical summary"]
    if any(k in note_content_lower for k in triggers_8):
        mock_tasks.append({
            "title": "Respect communication restriction",
            "desc": "The source note restricts patient communication. Do not send clinical summaries or call unless the stated condition is met.",
            "excerpt": get_excerpt(note_content, triggers_8),
            "type": "communication_restriction"
        })
        signals_detected.append("communication_restriction")
        
    triggers_9 = ["prefers spanish", "spanish reminders", "idioma español"]
    if any(k in note_content_lower for k in triggers_9):
        mock_tasks.append({
            "title": "Record administrative language preference",
            "desc": "The note indicates a Spanish preference for administrative reminders. Store as operational preference only.",
            "excerpt": get_excerpt(note_content, triggers_9),
            "type": "language_preference_recorded"
        })
        signals_detected.append("language_preference_recorded")
        
    triggers_10 = ["no medication changes", "no medication change"]
    if any(k in note_content_lower for k in triggers_10):
        signals_detected.append("medication_change_denied")
        
    triggers_11 = ["multiple demo patients", "mixes multiple", "combines several patients", "alex parker", "lina santos", "omar torres"]
    if any(k in note_content_lower for k in triggers_11):
        mock_tasks.append({
            "title": "Flag mixed-patient note for human review",
            "desc": "The source note appears to include multiple patients. Do not execute final tasks until a human splits or confirms patient ownership.",
            "excerpt": get_excerpt(note_content, triggers_11),
            "type": "mixed_patient_note_detected"
        })
        signals_detected.append("mixed_patient_note_detected")
        
    triggers_12 = ["human review required", "reviewed by a human", "require review", "flag"]
    if any(k in note_content_lower for k in triggers_12):
        signals_detected.append("human_review_required")

    if not mock_tasks:
        mock_tasks.append({
            "title": "Review operational note manually",
            "desc": "No safe operational signal was confidently detected. Human review is required.",
            "excerpt": "not available in mock extraction.",
            "type": "manual_review"
        })
        signals_detected.append("human_review_required")

    return mock_tasks, signals_detected

scenario_1 = """Demo clinic note — synthetic data only.

Patient: Ana Rivera Demo.
Context: post-visit admin cleanup after a short consultation. The clinician already spoke with the patient. This is not a diagnostic note and should not be used to create diagnosis, treatment, medication or patient-facing advice.

Messy staff note:
Ana left quickly after the visit. Dr. Martín said the clinical plan was already explained verbally and no medication changes were made today. Reception still needs to check whether the intake consent form was actually signed because the paper folder has a blank copy but the front desk system says ‘received’. Insurance information may be outdated; patient mentioned a new provider card but we did not scan it. Follow-up should probably be scheduled in around 10 days, but only after the clinician confirms the exact window. Patient prefers Spanish for administrative reminders. Please prepare a short internal visit summary for clinician review before the next appointment. Do not send a clinical summary to the patient yet. Do not add diagnosis. Do not add treatment recommendations. Human review required."""

scenario_4 = """Demo clinic note — synthetic data only.

Context: end-of-day admin cleanup note. Warning: this note mixes multiple demo patients and must be flagged for human review before final task execution.

Admin cleanup:
Alex Parker Demo needs follow-up booking after today’s visit. Lina Santos Demo is missing the intake form. Omar Torres Demo mentioned insurance changed and needs verification. This note combines several patients in one text, so the system should not pretend everything belongs to one patient. It should flag mixed-patient note risk, create only safe review tasks, and require a human to split or confirm the tasks before action. No diagnosis. No treatment recommendations. No medication changes."""

print("=== SCENARIO 1 ===")
tasks1, signals1 = mock_extract(scenario_1)
print("SIGNALS:")
for s in signals1: print(f"- {s}")
print("\nTASKS:")
for t in tasks1: 
    print(f"- {t['title']}\n  Evidence: {t['excerpt']}\n  Desc: {t['desc']}")

print("\n=== SCENARIO 4 ===")
tasks4, signals4 = mock_extract(scenario_4)
print("SIGNALS:")
for s in signals4: print(f"- {s}")
print("\nTASKS:")
for t in tasks4:
    print(f"- {t['title']}")
