from fastapi import APIRouter, HTTPException
from typing import List
from app.models.mcp_tool import MCPToolCallResponse
from app.repositories.repository_factory import get_mcp_tool_calls_repo

router = APIRouter(prefix="/mcp", tags=["mcp-tools"])

@router.get("/tool-calls", response_model=List[MCPToolCallResponse])
async def list_tool_calls():
    repo = get_mcp_tool_calls_repo()
    return await repo.list_tool_calls()

@router.get("/tool-calls/{tool_call_id}", response_model=MCPToolCallResponse)
async def get_tool_call(tool_call_id: str):
    repo = get_mcp_tool_calls_repo()
    call = await repo.get_tool_call(tool_call_id)
    if not call:
        raise HTTPException(status_code=404, detail="Tool call not found")
    return call
