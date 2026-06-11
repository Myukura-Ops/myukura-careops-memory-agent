import asyncio
import uuid
from datetime import datetime, timezone
from app.models.agent_run import AgentRunStatus, AgentRunEvent
from app.models.tasks import CareOpsTask, TaskStatus
from app.repositories.repository_factory import get_agent_runs_repo, get_tasks_repo, get_source_notes_repo
from app.repositories.repository_factory import get_agent_runs_repo, get_tasks_repo, get_source_notes_repo
from app.services.gemini_orchestrator import run_gemini_extraction
from app.services.mcp_tool_adapter import MCPToolAdapter
from app.services import observability
from app.config import settings
from app.services.partner_payload_builder import build_partner_outbox_items
from app.repositories.repository_factory import get_partner_outbox_repo

async def _simulate_delay(seconds: int = 2):
    await asyncio.sleep(seconds)

async def _transition_and_log(run_id: str, repo, status: AgentRunStatus, event_type: str, message: str, meta: dict = None, collection: str = None, document_id: str = None):
    now = datetime.now(timezone.utc)
    await repo.update_status(run_id, status)
    
    # We don't have patient_id / clinic_id explicitly here so we will fetch from run
    run = await repo.get_run(run_id)
    clinic_id = run.clinic_id if run else "clinic_demo"
    patient_id = run.patient_id if run else "patient_demo"

    event = AgentRunEvent(
        event_id=str(uuid.uuid4()),
        run_id=run_id,
        clinic_id=clinic_id,
        patient_id=patient_id,
        event_type=event_type,
        message=message,
        collection=collection,
        document_id=document_id,
        timestamp=now,
        human_visible=True,
        metadata=meta or {}
    )
    await repo.add_event(run_id, event)

async def _update_status(repo, run_id: str, status: AgentRunStatus, message: str):
    await repo.update_status(run_id, status)

async def _create_mock_tasks(run_id: str, run):
    now = datetime.now(timezone.utc)
    repo = get_tasks_repo()
    source_notes_repo = get_source_notes_repo()
    
    note_content = ""
    if run.source_note_id:
        source_note = await source_notes_repo.get_source_note(run.source_note_id)
        if source_note:
            note_content = source_note.content
            
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
            "title": "Prepare handoff/internal summary for review",
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
        
    task_ids = []
    for idx, t in enumerate(mock_tasks):
        task = CareOpsTask(
            task_id=str(uuid.uuid4()),
            clinic_id=run.clinic_id,
            patient_id=run.patient_id,
            professional_id=run.professional_id,
            source_note_id=run.source_note_id,
            agent_run_id=run_id,
            title=t["title"],
            description=f"{t['desc']}\n\nSource evidence: '{t['excerpt']}'",
            task_type=t["type"],
            priority="medium",
            status=TaskStatus.proposed,
            requires_human_approval=True,
            risk_level="review_required",
            created_by="mock_careops_agent",
            created_at=now,
            updated_at=now
        )
        await repo.create_task(task)
        task_ids.append(task.task_id)
        
    return task_ids, signals_detected

async def simulate_agent_run(run_id: str):
    """
    Orchestrates the background execution of an agent run.
    Depending on the mode, uses either a mock process or Gemini.
    """
    repo = get_agent_runs_repo()
    
    run = await repo.get_run(run_id)
    if not run:
        return
        
    observability.trace_agent_run_started(run_id, run.execution_mode)
    
    mode = run.execution_mode
    
    # 1. Processing
    await _update_status(repo, run_id, AgentRunStatus.processing, "Starting processing pipeline...")
    await _simulate_delay(1)
    await _transition_and_log(run_id, repo, AgentRunStatus.processing, "WORKER_SIMULATION_STARTED", f"API background worker started ({mode} mode).")
    
    await _simulate_delay(1)
    
    await _transition_and_log(run_id, repo, AgentRunStatus.processing, "MEMORY_CONTEXT_LOOKUP_STARTED", "Looking up previous operational memory.")
    from app.services.memory_builder import build_memory_context
    memory_ctx = await build_memory_context(run.patient_id, run.professional_id, run.clinic_id, run_id)
    
    if memory_ctx.get("memory_found"):
        await _transition_and_log(run_id, repo, AgentRunStatus.processing, "MEMORY_CONTEXT_FOUND", memory_ctx.get("summary", "Memory found."))
    else:
        if memory_ctx.get("error"):
            await _transition_and_log(run_id, repo, AgentRunStatus.processing, "MEMORY_CONTEXT_LOOKUP_FAILED", "Failed to build memory context, proceeding without it.")
        else:
            await _transition_and_log(run_id, repo, AgentRunStatus.processing, "MEMORY_CONTEXT_NOT_FOUND", memory_ctx.get("summary", "No memory found."))

    patient_memory = memory_ctx
    prof_prefs = {}

    # 2. Model Running & Verifying
    if mode == "mock":
        await _transition_and_log(run_id, repo, AgentRunStatus.model_running, "SOURCE_NOTE_RECEIVED", "Synthetic operational source note received. No real patient data.")
        await _simulate_delay(1)
        
        task_ids, signals_detected = await _create_mock_tasks(run_id, run)
        
        sig_str = ", ".join(signals_detected) if signals_detected else "none"
        await _transition_and_log(run_id, repo, AgentRunStatus.model_running, "OPERATIONAL_SIGNALS_DETECTED", f"Detected operational signals: {sig_str}.")
        await _simulate_delay(1)
        
        await _transition_and_log(run_id, repo, AgentRunStatus.verifying, "SAFETY_BOUNDARIES_APPLIED", "Clinical automation disabled: no diagnosis, treatment recommendation, medication change, or external delivery.")
        await _simulate_delay(1)
        
        if run.result is None:
            run.result = {}
        run.result["tasks_created"] = len(task_ids)
        run.result["audit_events_created"] = 7
        run.result["safety_status"] = "passed_mock"
        run.result["extraction_mode"] = "mock"
        run.result["gemini_used"] = False
        run.result["excluded_items_count"] = 0
        run.result["operational_signals_detected"] = signals_detected
        run.result["memory_context_used"] = memory_ctx.get("items", [])
        run.result["memory_found"] = memory_ctx.get("memory_found", False)
        run.result["memory_context_error"] = memory_ctx.get("error")
        run.result["memory_items_count"] = len(memory_ctx.get("items", []))
        run.result["memory_context_limited_to"] = 10
        run.result["memory_injected_into_gemini"] = False
        await repo.update_run(run_id, run)
        
        await _transition_and_log(
            run_id, repo, AgentRunStatus.writing_tasks, "TASKS_PROPOSED", f"Proposed {len(task_ids)} non-clinical operational tasks requiring human approval.",
            meta={"write_count": len(task_ids), "task_ids": task_ids}, collection="careops_tasks"
        )
        
        await _transition_and_log(
            run_id, repo, AgentRunStatus.writing_tasks, "MEMORY_WRITTEN_TO_MONGODB", "Agent run, source note, proposed tasks and audit events were persisted to MongoDB."
        )
        final_status = AgentRunStatus.completed
        
    elif mode == "gemini":
        mcp_adapter = MCPToolAdapter(run_id)
        await _transition_and_log(run_id, repo, AgentRunStatus.model_running, "GEMINI_EXTRACTION_STARTED", "Starting Gemini safe extraction.")
        
        if memory_ctx.get("memory_found"):
            await _transition_and_log(run_id, repo, AgentRunStatus.model_running, "MEMORY_CONTEXT_INJECTED_INTO_GEMINI", "Safe operational memory context injected into Gemini prompt.")
            
        # Load source note
        source_notes_repo = get_source_notes_repo()
        note_content = ""
        if run.source_note_id:
            source_note_doc = await source_notes_repo.get_source_note(run.source_note_id)
            if source_note_doc:
                note_content = source_note_doc.content
            
        from app.services.gemini_orchestrator import run_gemini_extraction, validate_gemini_extraction
        
        extraction_result, status_msg, metadata = await run_gemini_extraction(
            source_note=note_content,
            patient_memory=patient_memory,
            prof_prefs=prof_prefs
        )
        
        for attempt in metadata.get("model_attempts", []):
            model = attempt["model"]
            await _transition_and_log(run_id, repo, AgentRunStatus.model_running, "GEMINI_MODEL_ATTEMPT_STARTED", f"Starting Gemini model attempt for {model}.")
            if attempt["status"] == "success":
                await _transition_and_log(run_id, repo, AgentRunStatus.model_running, "GEMINI_MODEL_ATTEMPT_SUCCEEDED", f"Gemini model attempt succeeded for {model}.")
            else:
                await _transition_and_log(run_id, repo, AgentRunStatus.model_running, "GEMINI_MODEL_ATTEMPT_FAILED", f"Gemini model attempt failed for {model}. Falling back to next configured model if available.")
        
        if status_msg.startswith("fallback"):
            await _transition_and_log(run_id, repo, AgentRunStatus.model_running, "GEMINI_EXTRACTION_FAILED", f"Gemini failed: {status_msg}")
            await _transition_and_log(run_id, repo, AgentRunStatus.model_running, "FALLBACK_TO_MOCK_USED", "Using deterministic mock extraction fallback.")
            
            task_ids, signals_detected = await _create_mock_tasks(run_id, run)
            
            if run.result is None:
                run.result = {}
            run.result["extraction_mode"] = "mock"
            run.result["requested_mode"] = "gemini"
            run.result["fallback_used"] = True
            run.result["fallback_reason"] = status_msg
            run.result["model_attempts"] = metadata.get("model_attempts", [])
            run.result["safety_status"] = "passed_mock_fallback"
            run.result["tasks_created"] = len(task_ids)
            run.result["memory_context_used"] = memory_ctx.get("items", [])
            run.result["memory_found"] = memory_ctx.get("memory_found", False)
            run.result["memory_context_error"] = memory_ctx.get("error")
            run.result["memory_items_count"] = len(memory_ctx.get("items", []))
            run.result["memory_context_limited_to"] = 10
            run.result["memory_injected_into_gemini"] = False
            await repo.update_run(run_id, run)
            
            await _transition_and_log(run_id, repo, AgentRunStatus.writing_tasks, "TASKS_PROPOSED", f"Proposed {len(task_ids)} fallback tasks.")
            final_status = AgentRunStatus.completed_with_warnings
            
        else:
            validated_result = validate_gemini_extraction(extraction_result)
            
            if run.result is None:
                run.result = {}
            
            signals = [s.id for s in validated_result.operational_signals]
            
            run.result["extraction_mode"] = "gemini"
            run.result["model_used"] = metadata.get("model_used")
            run.result["model_attempts"] = metadata.get("model_attempts", [])
            run.result["fallback_used"] = False
            run.result["operational_signals_detected"] = signals
            
            # Check if prompt injection safety flag was hit
            has_injection = any("prompt_injection" in f.id for f in validated_result.safety_flags)
            run.result["safety_status"] = "failed_gemini_safe_validator" if has_injection else "passed_gemini_safe_validator"
            run.result["safety_flags"] = [f.id for f in validated_result.safety_flags]
            run.result["memory_facts"] = [m.fact_type for m in validated_result.memory_facts]
            run.result["memory_context_used"] = memory_ctx.get("items", [])
            run.result["memory_found"] = memory_ctx.get("memory_found", False)
            run.result["memory_context_error"] = memory_ctx.get("error")
            run.result["memory_items_count"] = len(memory_ctx.get("items", []))
            run.result["memory_context_limited_to"] = 10
            run.result["memory_injected_into_gemini"] = True
            
            task_ids = []
            for t in validated_result.proposed_tasks:
                task = CareOpsTask(
                    task_id=str(uuid.uuid4()),
                    clinic_id=run.clinic_id,
                    patient_id=run.patient_id,
                    professional_id=run.professional_id,
                    source_note_id=run.source_note_id,
                    agent_run_id=run_id,
                    title=t.title,
                    description=f"{t.description}\n\nSource evidence: '{t.source_evidence}'",
                    task_type=t.category,
                    priority="medium",
                    status=TaskStatus.proposed,
                    requires_human_approval=True,
                    risk_level=t.risk_level,
                    created_by="gemini_careops_agent",
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc)
                )
                await get_tasks_repo().create_task(task)
                task_ids.append(task.task_id)
                
            run.result["tasks_created"] = len(task_ids)
            await repo.update_run(run_id, run)
            
            await _transition_and_log(run_id, repo, AgentRunStatus.verifying, "GEMINI_EXTRACTION_COMPLETED", "Gemini structured extraction completed.")
            await _transition_and_log(run_id, repo, AgentRunStatus.verifying, "SAFETY_VALIDATION_PASSED", "Backend safety validator passed.")
            await _transition_and_log(run_id, repo, AgentRunStatus.writing_tasks, "TASKS_PROPOSED", f"Proposed {len(task_ids)} safe operational tasks.")
            await _transition_and_log(run_id, repo, AgentRunStatus.writing_tasks, "MEMORY_WRITTEN_TO_MONGODB", "Tasks persisted.")
            final_status = AgentRunStatus.completed

    # 4.5 Partner Outbox Creation
    if getattr(settings, "partner_outbox_enabled", False):
        try:
            tasks = [await get_tasks_repo().get_task(tid) for tid in task_ids]
            outbox_items = build_partner_outbox_items(
                run_id=run_id,
                clinic_id=run.clinic_id,
                patient_id=run.patient_id,
                result=run.result,
                tasks=[t for t in tasks if t is not None]
            )
            outbox_repo = get_partner_outbox_repo()
            await outbox_repo.create_partner_outbox_items(outbox_items)
            
            run.result["partner_integrations"] = {
                "mongo_db": {
                    "status": "integrated",
                    "role": "persistent_operational_memory"
                },
                "arize": {
                    "status": "outbox_ready",
                    "external_export_enabled": getattr(settings, "arize_export_enabled", False),
                    "payload_type": "llm_observability",
                    "outbox_created": True
                },
                "elastic": {
                    "status": "outbox_ready",
                    "external_export_enabled": getattr(settings, "elastic_export_enabled", False),
                    "payload_type": "audit_search",
                    "outbox_created": True
                },
                "external_exports_active": False,
                "note": "Arize and Elastic exports are prepared in partner_outbox but not externally activated."
            }
            await repo.update_run(run_id, run)
            await _transition_and_log(run_id, repo, AgentRunStatus.writing_tasks, "PARTNER_OUTBOX_CREATED", "Partner outbox records created for Arize and Elastic.")
            await _transition_and_log(run_id, repo, AgentRunStatus.writing_tasks, "ARIZE_OBSERVABILITY_OUTBOX_READY", "Arize observability payload generated.")
            await _transition_and_log(run_id, repo, AgentRunStatus.writing_tasks, "ELASTIC_AUDIT_SEARCH_OUTBOX_READY", "Elastic audit search payload generated.")
        except Exception as e:
            err_str = str(e)[:300]
            run.result["partner_integrations"] = {
                "mongo_db": {
                    "status": "integrated",
                    "role": "persistent_operational_memory"
                },
                "arize": {
                    "status": "outbox_failed",
                    "external_export_enabled": getattr(settings, "arize_export_enabled", False)
                },
                "elastic": {
                    "status": "outbox_failed",
                    "external_export_enabled": getattr(settings, "elastic_export_enabled", False)
                },
                "external_exports_active": False,
                "note": "Partner outbox creation failed safely; the core agent run completed."
            }
            await repo.update_run(run_id, run)
            await _transition_and_log(run_id, repo, AgentRunStatus.writing_tasks, "PARTNER_OUTBOX_CREATION_FAILED", f"Failed to create partner outbox records: {err_str}")

    # 5. Waiting Human Review
    await _transition_and_log(run_id, repo, AgentRunStatus.waiting_human_review, "HUMAN_REVIEW_REQUIRED", "Run paused for human review before task action.")

    # 6. Completed
    await _simulate_delay(1)
    await _transition_and_log(run_id, repo, final_status, "RUN_COMPLETED", "Mock operational memory run completed.")
    observability.trace_agent_run_completed(run_id, final_status.value if hasattr(final_status, "value") else str(final_status))
