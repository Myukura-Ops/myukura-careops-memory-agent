import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from app.models.partner_outbox import PartnerOutbox

def safe_demo_patient_id(patient_id: str) -> str:
    pid_lower = patient_id.lower()
    if "demo" in pid_lower or "synthetic" in pid_lower or "test" in pid_lower:
        return patient_id
    return "redacted_demo_patient"

def build_arize_observability_payload(
    *,
    run_id: str,
    clinic_id: str,
    patient_id: str,
    result: dict,
    tasks: list,
    audit_events: Optional[list] = None,
    created_at: Optional[datetime] = None
) -> dict:
    return {
        "run_id": run_id,
        "model_used": result.get("model_used", "unknown"),
        "model_attempts": result.get("model_attempts", []),
        "fallback_used": result.get("fallback_used", False),
        "extraction_mode": result.get("extraction_mode", "unknown"),
        "safety_status": result.get("safety_status", "unknown"),
        "prompt_injection_detected": any("prompt_injection" in flag for flag in result.get("safety_flags", [])),
        "memory_found": result.get("memory_found", False),
        "memory_items_count": result.get("memory_items_count", 0),
        "task_count": len(tasks),
        "human_review_required": True,
        "validator_status": result.get("safety_status", "unknown"),
        "created_at": (created_at or datetime.now(timezone.utc)).isoformat()
    }

def build_elastic_audit_search_payload(
    *,
    run_id: str,
    clinic_id: str,
    patient_id: str,
    result: dict,
    tasks: list,
    audit_events: Optional[list] = None,
    created_at: Optional[datetime] = None
) -> dict:
    task_titles = [getattr(t, "title", t.get("title", "") if isinstance(t, dict) else "")[:120] for t in tasks]
    task_statuses = [t.status.value if hasattr(t, "status") and hasattr(t.status, "value") else str(getattr(t, "status", t.get("status", "proposed") if isinstance(t, dict) else "proposed")) for t in tasks]
    
    event_types = []
    if audit_events:
        event_types = [e.event_type if hasattr(e, "event_type") else e.get("event_type", "") for e in audit_events]
    
    return {
        "run_id": run_id,
        "clinic_id": clinic_id,
        "patient_id": safe_demo_patient_id(patient_id),
        "extraction_mode": result.get("extraction_mode", "unknown"),
        "model_used": result.get("model_used", "unknown"),
        "fallback_used": result.get("fallback_used", False),
        "safety_status": result.get("safety_status", "unknown"),
        "safety_flags": result.get("safety_flags", []),
        "task_titles": task_titles,
        "task_statuses": task_statuses,
        "audit_event_types": event_types,
        "memory_found": result.get("memory_found", False),
        "memory_items_count": result.get("memory_items_count", 0),
        "created_at": (created_at or datetime.now(timezone.utc)).isoformat()
    }

def build_partner_outbox_items(
    *,
    run_id: str,
    clinic_id: str,
    patient_id: str,
    result: dict,
    tasks: list,
    audit_events: Optional[list] = None
) -> List[PartnerOutbox]:
    
    now = datetime.now(timezone.utc)
    
    arize_payload = build_arize_observability_payload(
        run_id=run_id, clinic_id=clinic_id, patient_id=patient_id, 
        result=result, tasks=tasks, audit_events=audit_events, created_at=now
    )
    
    elastic_payload = build_elastic_audit_search_payload(
        run_id=run_id, clinic_id=clinic_id, patient_id=patient_id, 
        result=result, tasks=tasks, audit_events=audit_events, created_at=now
    )
    
    safe_patient_id = safe_demo_patient_id(patient_id)
    
    arize_outbox = PartnerOutbox(
        outbox_id=str(uuid.uuid4()),
        run_id=run_id,
        clinic_id=clinic_id,
        patient_id=safe_patient_id,
        partner="arize",
        payload_type="llm_observability",
        status="pending",
        created_at=now,
        updated_at=now,
        payload=arize_payload
    )
    
    elastic_outbox = PartnerOutbox(
        outbox_id=str(uuid.uuid4()),
        run_id=run_id,
        clinic_id=clinic_id,
        patient_id=safe_patient_id,
        partner="elastic",
        payload_type="audit_search",
        status="pending",
        created_at=now,
        updated_at=now,
        payload=elastic_payload
    )
    
    return [arize_outbox, elastic_outbox]
