from typing import List, Literal, Optional
from pydantic import BaseModel, Field

class OperationalSignal(BaseModel):
    id: str = Field(..., description="The ID of the operational signal detected (e.g. follow_up_requested)")
    label: str = Field(..., description="Human-readable label of the signal")
    source_evidence: str = Field(..., description="Direct quote from the source note")
    confidence: str = Field("medium", description="Confidence level")

class ProposedOperationalTask(BaseModel):
    title: str = Field(..., description="Short title of the task")
    description: str = Field(..., description="Detailed description")
    source_evidence: str = Field(..., description="Direct quote from the source note justifying the task")
    requires_human_approval: bool = Field(True, description="Must always be true")
    category: str = Field("administrative", description="Must be administrative")
    risk_level: str = Field("low", description="Must be low")

class SafetyFlag(BaseModel):
    id: str = Field(..., description="ID of the safety rule triggered")
    label: str = Field(..., description="Human-readable reason")
    source_evidence: Optional[str] = Field(None, description="Related evidence if any")

class MemoryFact(BaseModel):
    fact_type: str = Field(..., description="Type of memory fact (e.g. language_preference)")
    value: str = Field(..., description="The value of the fact")
    source_evidence: str = Field(..., description="Quote from source note")

class GeminiSafeExtractionResult(BaseModel):
    operational_signals: List[OperationalSignal] = Field(..., description="Extracted signals")
    proposed_tasks: List[ProposedOperationalTask] = Field(..., description="Extracted non-clinical tasks")
    safety_flags: List[SafetyFlag] = Field(..., description="Safety boundaries flagged during extraction")
    memory_facts: List[MemoryFact] = Field(..., description="Facts to persist in memory")
    requires_human_review: bool = Field(True, description="Must be true")
    warnings: List[str] = Field([], description="Optional warnings")
    extraction_confidence: str = Field("medium", description="Confidence of extraction")
