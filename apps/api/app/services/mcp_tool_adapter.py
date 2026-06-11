import uuid
import time
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from app.models.tasks import CareOpsTask, TaskStatus
from app.models.agent_run import AgentRunEvent
from app.models.mcp_tool import MCPToolCallCreate, MCPToolStatus, MCPToolError
from app.repositories.repository_factory import get_mcp_tool_calls_repo, get_tasks_repo, get_agent_runs_repo
from app.services.safety_verifier import check_safety_violations
from app.services import observability

# This is the Controlled MongoDB Tool Adapter
# It exposes controlled tool interfaces that log MCP execution,
# but executes via local native Python repositories.

class MCPToolAdapter:
    def __init__(self, run_id: str):
        self.run_id = run_id
        self.repo = get_mcp_tool_calls_repo()
        
    async def _start_tool(self, tool_name: str, input_summary: Dict[str, Any]) -> str:
        tool_call_id = str(uuid.uuid4())
        call = MCPToolCallCreate(
            tool_call_id=tool_call_id,
            run_id=self.run_id,
            tool_name=tool_name,
            input_summary=input_summary
        )
        await self.repo.create_tool_call_started(call)
        
        # Audit log
        agent_repo = get_agent_runs_repo()
        await agent_repo.add_event(
            self.run_id,
            AgentRunEvent(
                event_id=str(uuid.uuid4()),
                run_id=self.run_id,
                event_type="MCP_TOOL_STARTED",
                message=f"Starting MCP Tool: {tool_name}",
                timestamp=datetime.now(timezone.utc),
                human_visible=True,
                metadata={"tool_call_id": tool_call_id, "adapter_type": "controlled_local_adapter"}
            )
        )
        return tool_call_id

    async def _fail_tool(self, tool_call_id: str, tool_name: str, error: str, latency_ms: int):
        await self.repo.mark_tool_call_failed(tool_call_id, error, latency_ms)
        agent_repo = get_agent_runs_repo()
        await agent_repo.add_event(
            self.run_id,
            AgentRunEvent(
                event_id=str(uuid.uuid4()),
                run_id=self.run_id,
                event_type="MCP_TOOL_FAILED",
                message=f"Failed MCP Tool: {tool_name}",
                timestamp=datetime.now(timezone.utc),
                human_visible=True,
                metadata={"tool_call_id": tool_call_id, "error": error}
            )
        )

    async def _block_tool(self, tool_call_id: str, tool_name: str, error: str, latency_ms: int):
        await self.repo.mark_tool_call_blocked(tool_call_id, error, latency_ms)
        agent_repo = get_agent_runs_repo()
        await agent_repo.add_event(
            self.run_id,
            AgentRunEvent(
                event_id=str(uuid.uuid4()),
                run_id=self.run_id,
                event_type="MCP_TOOL_BLOCKED",
                message=f"Blocked unsafe MCP Tool execution: {tool_name}",
                timestamp=datetime.now(timezone.utc),
                human_visible=True,
                metadata={"tool_call_id": tool_call_id, "error": error}
            )
        )

    async def _succeed_tool(self, tool_call_id: str, tool_name: str, output_summary: dict, collections: List[str], doc_ids: List[str], latency_ms: int):
        await self.repo.mark_tool_call_success(tool_call_id, output_summary, collections, doc_ids, latency_ms)
        agent_repo = get_agent_runs_repo()
        await agent_repo.add_event(
            self.run_id,
            AgentRunEvent(
                event_id=str(uuid.uuid4()),
                run_id=self.run_id,
                event_type="MCP_TOOL_SUCCEEDED",
                message=f"Successfully executed MCP Tool: {tool_name}",
                timestamp=datetime.now(timezone.utc),
                human_visible=True,
                metadata={"tool_call_id": tool_call_id, "collections": collections}
            )
        )

    async def call_search_patient_memory(self, patient_id: str) -> Dict[str, Any]:
        start = time.time()
        tool_call_id = await self._start_tool("search_patient_memory", {"patient_id": patient_id})
        try:
            # Mocking fetch
            output = {
                "patient_id": patient_id,
                "open_tasks_count": 0,
                "recent_task_titles": [],
                "operational_context": {"last_visit": "2026-05-10", "flags": ["needs_follow_up"]}
            }
            latency_ms = int((time.time() - start) * 1000)
            await self._succeed_tool(tool_call_id, "search_patient_memory", output, ["patients_demo", "careops_tasks"], [], latency_ms)
            observability.trace_mcp_tool_call(self.run_id, "search_patient_memory", "success", latency_ms)
            return output
        except Exception as e:
            latency_ms = int((time.time() - start) * 1000)
            await self._fail_tool(tool_call_id, "search_patient_memory", str(e), latency_ms)
            observability.trace_mcp_tool_call(self.run_id, "search_patient_memory", "error", latency_ms)
            raise e

    async def call_get_professional_preferences(self, professional_id: str) -> Dict[str, Any]:
        start = time.time()
        tool_call_id = await self._start_tool("get_professional_preferences", {"professional_id": professional_id})
        try:
            output = {
                "professional_id": professional_id,
                "handoff_style": "brief",
                "task_priority_rules": {"preferred_priority": "medium"},
                "review_mode": "human_approval_required"
            }
            latency_ms = int((time.time() - start) * 1000)
            await self._succeed_tool(tool_call_id, "get_professional_preferences", output, ["professional_preferences"], [], latency_ms)
            observability.trace_mcp_tool_call(self.run_id, "get_professional_preferences", "success", latency_ms)
            return output
        except Exception as e:
            latency_ms = int((time.time() - start) * 1000)
            await self._fail_tool(tool_call_id, "get_professional_preferences", str(e), latency_ms)
            observability.trace_mcp_tool_call(self.run_id, "get_professional_preferences", "error", latency_ms)
            raise e

    async def call_create_careops_task(self, clinic_id: str, patient_id: str, professional_id: str, source_note_id: str, title: str, description: str, task_type: str, priority: str, risk_level: str) -> Dict[str, Any]:
        start = time.time()
        
        valid_task_types = [
            "follow_up_scheduling", "admin_documentation", "missing_form_check", 
            "internal_reminder", "handoff_preparation", "requires_clinician_review"
        ]
        
        if task_type not in valid_task_types:
            task_type = "admin_documentation"

        input_summary = {
            "safe_summary": f"Create proposed {task_type} task.",
            "task_type": task_type,
            "priority": priority,
            "redacted": True
        }
        tool_call_id = await self._start_tool("create_careops_task", input_summary)
        
        # Safety verification
        violation = check_safety_violations(title, description)
        if violation:
            latency_ms = int((time.time() - start) * 1000)
            error_msg = f"Safety verifier blocked execution: {violation}"
            await self._block_tool(tool_call_id, "create_careops_task", error_msg, latency_ms)
            observability.trace_mcp_tool_call(self.run_id, "create_careops_task", "blocked", latency_ms)
            raise Exception(f"MCP_UNSAFE_OPERATION_BLOCKED: {error_msg}")

        try:
            tasks_repo = get_tasks_repo()
            now = datetime.now(timezone.utc)
            task_id = str(uuid.uuid4())
            task = CareOpsTask(
                task_id=task_id,
                clinic_id=clinic_id,
                patient_id=patient_id,
                professional_id=professional_id,
                source_note_id=source_note_id,
                agent_run_id=self.run_id,
                title=title,
                description=description,
                task_type=task_type,
                priority=priority,
                status=TaskStatus.proposed,
                requires_human_approval=True,
                risk_level="low",
                created_by="mock_careops_agent",
                created_at=now,
                updated_at=now
            )
            await tasks_repo.create_task(task)
            
            output = {
                "task_id": task_id,
                "status": "proposed",
                "requires_human_approval": True
            }
            latency_ms = int((time.time() - start) * 1000)
            await self._succeed_tool(tool_call_id, "create_careops_task", output, ["careops_tasks"], [task_id], latency_ms)
            observability.trace_mcp_tool_call(self.run_id, "create_careops_task", "success", latency_ms)
            return output
        except Exception as e:
            latency_ms = int((time.time() - start) * 1000)
            await self._fail_tool(tool_call_id, "create_careops_task", str(e), latency_ms)
            observability.trace_mcp_tool_call(self.run_id, "create_careops_task", "error", latency_ms)
            raise e

    async def call_write_audit_log(self, clinic_id: str, patient_id: str, event_type: str, message: str, metadata: dict) -> Dict[str, Any]:
        start = time.time()
        input_summary = {
            "safe_summary": f"Audit log generated for event: {event_type}",
            "event_type": event_type,
            "redacted": True
        }
        tool_call_id = await self._start_tool("write_audit_log", input_summary)
        try:
            agent_repo = get_agent_runs_repo()
            event_id = str(uuid.uuid4())
            event = AgentRunEvent(
                event_id=event_id,
                run_id=self.run_id,
                clinic_id=clinic_id,
                patient_id=patient_id,
                event_type=event_type,
                message=message,
                timestamp=datetime.now(timezone.utc),
                human_visible=True,
                metadata=metadata
            )
            await agent_repo.add_event(self.run_id, event)
            
            output = {"audit_id": event_id}
            latency_ms = int((time.time() - start) * 1000)
            await self._succeed_tool(tool_call_id, "write_audit_log", output, ["agent_audit_logs"], [event_id], latency_ms)
            observability.trace_mcp_tool_call(self.run_id, "write_audit_log", "success", latency_ms)
            return output
        except Exception as e:
            latency_ms = int((time.time() - start) * 1000)
            await self._fail_tool(tool_call_id, "write_audit_log", str(e), latency_ms)
            observability.trace_mcp_tool_call(self.run_id, "write_audit_log", "error", latency_ms)
            raise e
