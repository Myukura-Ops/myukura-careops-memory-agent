from typing import List, Optional, Dict
from datetime import datetime, timezone
import uuid

from app.models.mcp_tool import MCPToolCall, MCPToolCallCreate, MCPToolStatus

class InMemoryMCPToolCallsRepository:
    def __init__(self):
        self._store: Dict[str, MCPToolCall] = {}
        
    async def create_tool_call_started(self, tool_call: MCPToolCallCreate) -> MCPToolCall:
        now = datetime.now(timezone.utc)
        call_doc = MCPToolCall(
            tool_call_id=tool_call.tool_call_id,
            run_id=tool_call.run_id,
            tool_name=tool_call.tool_name,
            status=MCPToolStatus.started,
            input_summary=tool_call.input_summary,
            output_summary=None,
            collections_touched=[],
            document_ids=[],
            latency_ms=None,
            error=None,
            adapter_type=tool_call.adapter_type,
            official_mcp=tool_call.official_mcp,
            created_at=now
        )
        self._store[tool_call.tool_call_id] = call_doc
        return call_doc

    async def mark_tool_call_success(self, tool_call_id: str, output_summary: dict, collections: List[str], doc_ids: List[str], latency_ms: int):
        doc = self._store.get(tool_call_id)
        if doc:
            doc.status = MCPToolStatus.success
            doc.output_summary = output_summary
            doc.collections_touched = collections
            doc.document_ids = doc_ids
            doc.latency_ms = latency_ms
        
    async def mark_tool_call_failed(self, tool_call_id: str, error: str, latency_ms: int):
        doc = self._store.get(tool_call_id)
        if doc:
            doc.status = MCPToolStatus.failed
            doc.error = error
            doc.latency_ms = latency_ms

    async def mark_tool_call_blocked(self, tool_call_id: str, error: str, latency_ms: int):
        doc = self._store.get(tool_call_id)
        if doc:
            doc.status = MCPToolStatus.blocked
            doc.error = error
            doc.latency_ms = latency_ms

    async def list_tool_calls(self, run_id: Optional[str] = None) -> List[MCPToolCall]:
        results = []
        for doc in self._store.values():
            if run_id and doc.run_id != run_id:
                continue
            results.append(doc)
        return sorted(results, key=lambda x: x.created_at, reverse=True)

    async def get_tool_call(self, tool_call_id: str) -> Optional[MCPToolCall]:
        return self._store.get(tool_call_id)
