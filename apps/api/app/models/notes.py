from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class SourceNote(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    note_id: str
    clinic_id: str
    patient_id: str
    professional_id: str
    agent_run_id: str
    source_type: str
    content: str
    content_preview: str
    language: str
    safety_flags: List[str] = []
    created_at: datetime
