import uuid
from typing import Dict, List, Optional
from datetime import datetime, timezone
from app.models.agent_run import AgentRunDetail, AgentRunEvent, AgentRunStatus

# Phase 1 only. Replace with MongoDB repository in Phase 2.

_runs_store: Dict[str, AgentRunDetail] = {}
_events_store: Dict[str, List[AgentRunEvent]] = {}

async def create_run(run: AgentRunDetail) -> AgentRunDetail:
    _runs_store[run.run_id] = run
    _events_store[run.run_id] = []
    return run

async def get_run(run_id: str) -> Optional[AgentRunDetail]:
    return _runs_store.get(run_id)

async def list_runs() -> List[AgentRunDetail]:
    # Return recent runs, sorted by created_at descending
    return sorted(list(_runs_store.values()), key=lambda x: x.created_at, reverse=True)

async def get_runs_by_patient(patient_id: str, limit: int = 10) -> List[AgentRunDetail]:
    runs = [r for r in _runs_store.values() if r.patient_id == patient_id]
    runs = sorted(runs, key=lambda x: x.created_at, reverse=True)
    return runs[:limit]

async def update_status(run_id: str, status: AgentRunStatus) -> Optional[AgentRunDetail]:
    run = _runs_store.get(run_id)
    if run:
        run.status = status
        run.updated_at = datetime.now(timezone.utc)
    return run

async def update_run(run_id: str, run: AgentRunDetail) -> None:
    _runs_store[run_id] = run

async def add_event(run_id: str, event: AgentRunEvent) -> None:
    if run_id not in _events_store:
        _events_store[run_id] = []
    _events_store[run_id].append(event)

async def get_events(run_id: str) -> List[AgentRunEvent]:
    return _events_store.get(run_id, [])
