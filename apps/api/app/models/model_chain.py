from typing import Optional
from pydantic import BaseModel

class ModelAttemptMetadata(BaseModel):
    model: str
    role: str  # "primary", "fallback", "degraded"
    status: str  # "success", "failed", "timeout", "invalid_json", "disabled"
    latency_ms: int
    error_type: Optional[str] = None
