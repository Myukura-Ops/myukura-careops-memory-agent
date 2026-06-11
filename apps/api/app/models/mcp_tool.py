from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
from enum import Enum
from datetime import datetime

class MCPToolStatus(str, Enum):
    started = "started"
    success = "success"
    failed = "failed"
    blocked = "blocked"

class MCPToolCallCreate(BaseModel):
    tool_call_id: str
    run_id: str
    tool_name: str
    input_summary: Dict[str, Any]
    official_mcp: bool = False
    adapter_type: str = "controlled_local_adapter"

class MCPToolCall(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    tool_call_id: str
    run_id: str
    tool_name: str
    status: MCPToolStatus
    input_summary: Dict[str, Any]
    output_summary: Optional[Dict[str, Any]] = None
    collections_touched: List[str] = []
    document_ids: List[str] = []
    latency_ms: Optional[int] = None
    error: Optional[str] = None
    adapter_type: str
    official_mcp: bool
    created_at: datetime
    
class MCPToolCallResponse(MCPToolCall):
    pass

class MCPToolError(BaseModel):
    error_type: str
    message: str
    suggestion: str
    retryable: bool
    status: str
