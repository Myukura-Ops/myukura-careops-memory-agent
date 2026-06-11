from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class AgentAuditLog(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    audit_id: str
    run_id: str
    clinic_id: str
    patient_id: str
    event_type: str
    message: str
    collection_name: Optional[str] = Field(alias="collection", default=None)
    document_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    human_visible: bool
    timestamp: datetime
