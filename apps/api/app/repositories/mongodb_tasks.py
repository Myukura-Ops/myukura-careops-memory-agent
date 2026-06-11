from typing import List, Optional
from datetime import datetime, timezone
import uuid
from app.models.tasks import CareOpsTask, TaskStatus, TaskStatusHistory
from app.repositories import mongodb_client

async def create_task(task: CareOpsTask) -> CareOpsTask:
    task_dict = task.model_dump(by_alias=True, exclude_none=True)
    await mongodb_client.db["careops_tasks"].insert_one(task_dict)
    
    # create initial history
    now = datetime.now(timezone.utc)
    history = TaskStatusHistory(
        history_id=str(uuid.uuid4()),
        task_id=task.task_id,
        previous_status=task.status,
        new_status=task.status,
        changed_by=task.created_by,
        reason="Initial task creation",
        created_at=now
    )
    await mongodb_client.db["task_status_history"].insert_one(history.model_dump(by_alias=True, exclude_none=True))
    
    return task

async def get_task(task_id: str) -> Optional[CareOpsTask]:
    doc = await mongodb_client.db["careops_tasks"].find_one({"task_id": task_id})
    if doc:
        doc.pop("_id", None)
        return CareOpsTask(**doc)
    return None

async def list_tasks(clinic_id: Optional[str] = None) -> List[CareOpsTask]:
    query = {}
    if clinic_id:
        query["clinic_id"] = clinic_id
    cursor = mongodb_client.db["careops_tasks"].find(query).sort("created_at", -1).limit(100)
    tasks = []
    async for doc in cursor:
        doc.pop("_id", None)
        tasks.append(CareOpsTask(**doc))
    return tasks

async def update_task_status(task_id: str, new_status: TaskStatus, changed_by: str, reason: Optional[str] = None) -> Optional[CareOpsTask]:
    now = datetime.now(timezone.utc)
    
    # Fetch current task to validate transition
    doc = await mongodb_client.db["careops_tasks"].find_one({"task_id": task_id})
    if not doc:
        return None
        
    old_status = doc["status"]
    
    # Validations based on constraints
    valid_transitions = {
        TaskStatus.proposed: [TaskStatus.approved, TaskStatus.rejected],
        TaskStatus.approved: [TaskStatus.in_progress, TaskStatus.blocked],
        TaskStatus.blocked: [TaskStatus.approved],
        TaskStatus.in_progress: [TaskStatus.done],
        TaskStatus.rejected: [],
        TaskStatus.done: []
    }
    
    if new_status not in valid_transitions.get(TaskStatus(old_status), []):
        raise ValueError(f"INVALID_STATUS_TRANSITION: Cannot transition from {old_status} to {new_status}")
    
    result = await mongodb_client.db["careops_tasks"].find_one_and_update(
        {"task_id": task_id},
        {"$set": {"status": new_status, "updated_at": now}},
        return_document=True
    )
    
    if result:
        history = TaskStatusHistory(
            history_id=str(uuid.uuid4()),
            task_id=task_id,
            previous_status=old_status,
            new_status=new_status,
            changed_by=changed_by,
            reason=reason,
            created_at=now
        )
        await mongodb_client.db["task_status_history"].insert_one(history.model_dump(by_alias=True, exclude_none=True))
        result.pop("_id", None)
        return CareOpsTask(**result)
    
    return None

async def get_tasks_by_patient(patient_id: str) -> List[CareOpsTask]:
    cursor = mongodb_client.db["careops_tasks"].find({"patient_id": patient_id}).sort("created_at", -1).limit(50)
    tasks = []
    async for doc in cursor:
        doc.pop("_id", None)
        tasks.append(CareOpsTask(**doc))
    return tasks
