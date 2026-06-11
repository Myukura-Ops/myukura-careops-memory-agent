import uuid
from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

from app.config import settings
from app.models.agent_run import (
    AgentRunCreateRequest, AgentRunResponse, AgentRunStatus, 
    AgentRunDetail, AgentRunEvent, StructuredErrorResponse
)
from app.models.notes import SourceNote
from app.repositories.repository_factory import get_agent_runs_repo, get_source_notes_repo, get_mcp_tool_calls_repo
from app.services import task_queue

router = APIRouter(prefix="/agent-runs", tags=["agent-runs"])

@router.post("/", response_model=AgentRunResponse)
async def create_agent_run(request: AgentRunCreateRequest, background_tasks: BackgroundTasks):

    if len(request.source_note) > settings.max_source_note_chars:
        error_resp = StructuredErrorResponse(
            error_type="INPUT_TOO_LARGE",
            message="Source note exceeds the 6,000 character demo limit.",
            suggestion="Use a shorter synthetic approved note for the demo.",
            retryable=False
        )
        return JSONResponse(status_code=413, content=error_resp.model_dump())
        
    run_id = str(uuid.uuid4())
    note_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    
    # Create the source note
    source_note = SourceNote(
        note_id=note_id,
        clinic_id=request.clinic_id,
        patient_id=request.patient_id,
        professional_id=request.professional_id,
        agent_run_id=run_id,
        source_type="demo_synthetic",
        content=request.source_note,
        content_preview=request.source_note[:100] + "..." if len(request.source_note) > 100 else request.source_note,
        language="en",
        created_at=now
    )
    source_repo = get_source_notes_repo()
    await source_repo.create_source_note(source_note)
    
    # Create the run in the repository
    run = AgentRunDetail(
        run_id=run_id,
        clinic_id=request.clinic_id,
        patient_id=request.patient_id,
        professional_id=request.professional_id,
        source_note_id=note_id,
        status=AgentRunStatus.queued,
        execution_mode=request.mode,
        state_backend=settings.state_backend,
        queue={
            "provider": "background_queue",
            "task_name": f"run-{run_id}",
            "attempt": 1
        },
        worker={
            "mode": "api_background_simulation",
            "service": "careops-api",
            "orchestrator": "gemini_orchestrator" if request.mode == "gemini" else "deterministic_orchestrator"
        },
        model_chain=[],
        tools_called=[],
        result={
            "tasks_created": 0,
            "audit_events_created": 0,
            "safety_status": "pending",
            "extraction_mode": request.mode,
            "gemini_used": request.mode == "gemini",
            "excluded_items_count": 0
        },
        created_at=now,
        updated_at=now
    )
    repo = get_agent_runs_repo()
    await repo.create_run(run)
    
    # Add initial event
    event = AgentRunEvent(
        event_id=str(uuid.uuid4()),
        run_id=run_id,
        event_type="AGENT_RUN_CREATED",
        message="Agent run has been queued for processing.",
        timestamp=now,
        human_visible=True,
        metadata={"phase": "2A"}
    )
    await repo.add_event(run_id, event)
    
    # Enqueue background processing
    task_queue.enqueue_agent_run(run_id, background_tasks)
    
    return AgentRunResponse(
        run_id=run_id,
        status=AgentRunStatus.queued,
        message="Agent run created and queued successfully.",
        created_at=now,
        updated_at=now
    )

@router.get("")
async def list_agent_runs():
    repo = get_agent_runs_repo()
    return await repo.list_runs()

@router.get("/{run_id}", response_model=AgentRunDetail)
async def get_agent_run(run_id: str):
    repo = get_agent_runs_repo()
    run = await repo.get_run(run_id)
    if not run:
        raise HTTPException(
            status_code=404, 
            detail={
                "error_type": "RUN_NOT_FOUND",
                "message": f"Run {run_id} not found",
                "suggestion": "Check the run ID",
                "retryable": False,
                "status": "failed"
            }
        )
    
    # Dynamically resolve partner outbox statuses
    if run.result and "partner_integrations" in run.result:
        try:
            from app.repositories.repository_factory import get_partner_outbox_repo
            outbox_repo = get_partner_outbox_repo()
            outbox_items = await outbox_repo.get_partner_outbox_by_run(run_id)
            for item in outbox_items:
                partner = item.partner
                if partner in run.result["partner_integrations"]:
                    run.result["partner_integrations"][partner]["status"] = (
                        "outbox_ready" if item.status == "pending" else f"outbox_{item.status}"
                    )
        except Exception:
            pass
            
    return run

@router.get("/{run_id}/model-chain")
async def get_run_model_chain(run_id: str):
    repo = get_agent_runs_repo()
    run = await repo.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return {"run_id": run_id, "model_chain": run.model_chain}

@router.get("/{run_id}/events", response_model=List[AgentRunEvent])
async def get_agent_run_events(run_id: str):
    repo = get_agent_runs_repo()
    run = await repo.get_run(run_id)
    if not run:
        error_resp = StructuredErrorResponse(
            error_type="RUN_NOT_FOUND",
            message="The requested run could not be found.",
            suggestion="Check the run ID.",
            retryable=False
        )
        return JSONResponse(status_code=404, content=error_resp.model_dump())
    return await repo.get_events(run_id)

from app.models.mcp_tool import MCPToolCallResponse
@router.get("/{run_id}/mcp-tool-calls", response_model=List[MCPToolCallResponse])
async def get_agent_run_mcp_tool_calls(run_id: str):
    repo = get_agent_runs_repo()
    run = await repo.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    mcp_repo = get_mcp_tool_calls_repo()
    return await mcp_repo.list_tool_calls(run_id=run_id)
