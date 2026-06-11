from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime

class AgentRunStatus(str, Enum):
    queued = "queued"
    processing = "processing"
    model_running = "model_running"
    verifying = "verifying"
    writing_tasks = "writing_tasks"
    waiting_human_review = "waiting_human_review"
    completed = "completed"
    completed_with_warnings = "completed_with_warnings"
    failed = "failed"

class AgentRunCreateRequest(BaseModel):
    clinic_id: str
    patient_id: str
    professional_id: str
    source_note: str
    mode: str = "deterministic"

class AgentRunResponse(BaseModel):
    run_id: str
    status: AgentRunStatus
    message: str
    created_at: datetime
    updated_at: datetime

class AgentRunEvent(BaseModel):
    event_id: str
    run_id: str
    event_type: str
    message: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

class AgentRunDetail(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    run_id: str
    clinic_id: str
    patient_id: str
    professional_id: str
    source_note_id: str
    status: AgentRunStatus
    execution_mode: str
    state_backend: str
    queue: Dict[str, Any]
    worker: Dict[str, Any]
    model_chain: List[Dict[str, Any]]
    tools_called: List[str] = []
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime



class StructuredErrorResponse(BaseModel):
    error_type: str
    message: str
    suggestion: str
    retryable: bool
    status: str = "failed"
