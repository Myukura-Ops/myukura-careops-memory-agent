from typing import Dict, List, Optional
from datetime import datetime, timezone
from app.models.agent_run import AgentRunDetail, AgentRunEvent, AgentRunStatus
from app.repositories import mongodb_client

async def create_run(run: AgentRunDetail) -> AgentRunDetail:
    run_dict = run.model_dump(by_alias=True, exclude_none=True)
    # The events array is not stored in the agent_runs document in MongoDB directly,
    # as they are stored in the agent_audit_logs collection. So we remove events.
    if "events" in run_dict:
        del run_dict["events"]
    
    await mongodb_client.db["agent_runs"].insert_one(run_dict)
    return run

async def get_run(run_id: str) -> Optional[AgentRunDetail]:
    doc = await mongodb_client.db["agent_runs"].find_one({"run_id": run_id})
    if not doc:
        return None
    # we don't fetch events here by default, the events are fetched via get_events
    doc["events"] = []
    doc.pop("_id", None)
    return AgentRunDetail(**doc)

async def list_runs() -> List[AgentRunDetail]:
    cursor = mongodb_client.db["agent_runs"].find({}).sort("created_at", -1).limit(50)
    runs = []
    async for doc in cursor:
        doc["events"] = []
        doc.pop("_id", None)
        runs.append(AgentRunDetail(**doc))
    return runs

async def update_status(run_id: str, status: AgentRunStatus) -> Optional[AgentRunDetail]:
    now = datetime.now(timezone.utc)
    result = await mongodb_client.db["agent_runs"].find_one_and_update(
        {"run_id": run_id},
        {"$set": {"status": status, "updated_at": now}},
        return_document=True
    )
    if result:
        result["events"] = []
        result.pop("_id", None)
        return AgentRunDetail(**result)
    return None

async def update_run(run_id: str, run: AgentRunDetail) -> None:
    now = datetime.now(timezone.utc)
    run.updated_at = now
    run_dict = run.model_dump(by_alias=True, exclude_none=True)
    if "events" in run_dict:
        del run_dict["events"]
    await mongodb_client.db["agent_runs"].update_one(
        {"run_id": run_id},
        {"$set": run_dict}
    )

async def add_event(run_id: str, event: AgentRunEvent) -> None:
    event_dict = event.model_dump(by_alias=True, exclude_none=True)
    await mongodb_client.db["agent_audit_logs"].insert_one(event_dict)

async def get_events(run_id: str) -> List[AgentRunEvent]:
    cursor = mongodb_client.db["agent_audit_logs"].find({"run_id": run_id}).sort("timestamp", 1)
    events = []
    async for doc in cursor:
        doc.pop("_id", None)
        events.append(AgentRunEvent(**doc))
    return events

async def get_runs_by_patient(patient_id: str) -> List[AgentRunDetail]:
    cursor = mongodb_client.db["agent_runs"].find({"patient_id": patient_id}).sort("created_at", -1).limit(50)
    runs = []
    async for doc in cursor:
        doc["events"] = []
        doc.pop("_id", None)
        runs.append(AgentRunDetail(**doc))
    return runs
