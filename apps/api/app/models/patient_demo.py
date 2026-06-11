from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ClinicSettings(BaseModel):
    require_human_approval: bool = True
    allow_real_delivery: bool = False
    default_language: str = "en"

class Clinic(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    clinic_id: str
    name: str
    mode: str
    region: str
    settings: ClinicSettings
    created_at: datetime
    updated_at: datetime

class PatientDemo(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    patient_id: str
    clinic_id: str
    display_name: str
    language: str
    tags: List[str] = []
    operational_context: str
    created_at: datetime
    updated_at: datetime

class ProfessionalPreferences(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    professional_id: str
    clinic_id: str
    handoff_style: str
    task_priority_rules: str
    language_preference: str
    review_mode: str
    created_at: datetime
    updated_at: datetime
