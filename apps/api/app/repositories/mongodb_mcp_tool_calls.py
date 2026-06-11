from typing import List, Optional
from datetime import datetime, timezone
import uuid

from app.models.mcp_tool import MCPToolCall, MCPToolCallCreate, MCPToolStatus
from app.repositories.mongodb_client import db

class MongoDBMCPToolCallsRepository:
    def __init__(self):
        self.collection = db["mcp_tool_calls"]
        
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
        await self.collection.insert_one(call_doc.model_dump(by_alias=True, exclude_none=True))
        return call_doc

    async def mark_tool_call_success(self, tool_call_id: str, output_summary: dict, collections: List[str], doc_ids: List[str], latency_ms: int):
        await self.collection.update_one(
            {"tool_call_id": tool_call_id},
            {
                "$set": {
                    "status": MCPToolStatus.success.value,
                    "output_summary": output_summary,
                    "collections_touched": collections,
                    "document_ids": doc_ids,
                    "latency_ms": latency_ms
                }
            }
        )
        
    async def mark_tool_call_failed(self, tool_call_id: str, error: str, latency_ms: int):
        await self.collection.update_one(
            {"tool_call_id": tool_call_id},
            {
                "$set": {
                    "status": MCPToolStatus.failed.value,
                    "error": error,
                    "latency_ms": latency_ms
                }
            }
        )

    async def mark_tool_call_blocked(self, tool_call_id: str, error: str, latency_ms: int):
        await self.collection.update_one(
            {"tool_call_id": tool_call_id},
            {
                "$set": {
                    "status": MCPToolStatus.blocked.value,
                    "error": error,
                    "latency_ms": latency_ms
                }
            }
        )

    async def list_tool_calls(self, run_id: Optional[str] = None) -> List[MCPToolCall]:
        query = {}
        if run_id:
            query["run_id"] = run_id
        cursor = self.collection.find(query).sort("created_at", -1).limit(50)
        results = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            results.append(MCPToolCall(**doc))
        return results

    async def get_tool_call(self, tool_call_id: str) -> Optional[MCPToolCall]:
        doc = await self.collection.find_one({"tool_call_id": tool_call_id})
        if doc:
            doc["_id"] = str(doc["_id"])
            return MCPToolCall(**doc)
        return None
