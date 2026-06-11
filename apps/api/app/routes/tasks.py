from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List

from app.models.tasks import CareOpsTask, TaskStatus
from app.models.agent_run import StructuredErrorResponse
from app.repositories.repository_factory import get_tasks_repo

router = APIRouter(prefix="/tasks", tags=["tasks"])

class TaskStatusUpdateRequest(BaseModel):
    status: TaskStatus

@router.get("", response_model=List[CareOpsTask])
async def list_tasks(clinic_id: str = "clinic_demo"):
    repo = get_tasks_repo()
    return await repo.list_tasks(clinic_id=clinic_id)

@router.get("/{task_id}", response_model=CareOpsTask)
async def get_task(task_id: str):
    repo = get_tasks_repo()
    task = await repo.get_task(task_id)
    if not task:
        err = StructuredErrorResponse(
            error_type="TASK_NOT_FOUND",
            message="Task not found.",
            suggestion="Verify task ID.",
            retryable=False
        )
        return JSONResponse(status_code=404, content=err.model_dump())
    return task

from app.repositories import mongodb_demo_quotas

@router.patch("/{task_id}/status", response_model=CareOpsTask)
async def update_task_status(task_id: str, request: TaskStatusUpdateRequest):
    await mongodb_demo_quotas.check_task_mutation_quota()
    repo = get_tasks_repo()
    try:
        updated = await repo.update_task_status(task_id, request.status, changed_by="prof_demo", reason="UI Update")
        if not updated:
            err = StructuredErrorResponse(
                error_type="TASK_NOT_FOUND",
                message="Task not found.",
                suggestion="Verify task ID.",
                retryable=False
            )
            return JSONResponse(status_code=404, content=err.model_dump())
        return updated
    except ValueError as e:
        if "INVALID_STATUS_TRANSITION" in str(e):
            err = StructuredErrorResponse(
                error_type="INVALID_STATUS_TRANSITION",
                message=str(e),
                suggestion="Check allowed task status transitions.",
                retryable=False
            )
            return JSONResponse(status_code=400, content=err.model_dump())
        raise e
