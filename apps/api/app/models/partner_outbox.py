from pydantic import BaseModel
from typing import Optional, Literal, Dict, Any
from datetime import datetime

class PartnerOutbox(BaseModel):
    outbox_id: str
    run_id: str
    clinic_id: str
    patient_id: str
    partner: Literal["arize", "elastic"]
    payload_type: Literal["llm_observability", "audit_search"]
    status: Literal["pending", "sent", "failed", "skipped"] = "pending"
    attempt_count: int = 0
    max_attempts: int = 3
    next_attempt_at: Optional[datetime] = None
    last_error: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    sent_at: Optional[datetime] = None
    payload: Dict[str, Any]
