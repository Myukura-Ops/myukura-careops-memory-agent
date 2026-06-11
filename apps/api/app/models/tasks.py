from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TaskStatus(str, Enum):
    proposed = "proposed"
    approved = "approved"
    rejected = "rejected"
    in_progress = "in_progress"
    blocked = "blocked"
    done = "done"

class CareOpsTask(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    task_id: str
    clinic_id: str
    patient_id: str
    professional_id: str
    source_note_id: str
    agent_run_id: str
    title: str
    description: str
    task_type: str
    priority: str
    status: TaskStatus
    requires_human_approval: bool
    risk_level: str
    due_date: Optional[datetime] = None
    created_by: str
    created_at: datetime
    updated_at: datetime

class TaskStatusHistory(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    history_id: str
    task_id: str
    previous_status: TaskStatus
    new_status: TaskStatus
    changed_by: str
    reason: Optional[str] = None
    created_at: datetime
