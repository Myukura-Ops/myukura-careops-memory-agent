import logging
from typing import Any, Dict, List, Optional, Tuple

from app.config import settings
from app.repositories.repository_factory import get_tasks_repo, get_agent_runs_repo

logger = logging.getLogger(__name__)

MEMORY_FACT_KEYWORDS = ["language", "communication", "portal", "form", "consent", "insurance", "preference"]


async def _fetch_records_native(patient_id: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Fetch memory source records through the controlled native adapter."""
    tasks_repo = get_tasks_repo()
    runs_repo = get_agent_runs_repo()
    tasks = await tasks_repo.get_tasks_by_patient(patient_id)
    runs = await runs_repo.get_runs_by_patient(patient_id)
    # mode="json" normalizes enums and datetimes to plain JSON values,
    # matching the shape returned by the MCP path.
    return (
        [t.model_dump(mode="json") for t in tasks],
        [r.model_dump(mode="json") for r in runs],
    )


async def _fetch_records_mcp(patient_id: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Fetch memory source records through the official MongoDB MCP Server (read-only)."""
    from app.services.mongodb_mcp_client import mcp_find

    tasks = await mcp_find(
        "careops_tasks",
        {"patient_id": patient_id},
        limit=50,
        sort={"created_at": -1},
    )
    runs = await mcp_find(
        "agent_runs",
        {"patient_id": patient_id},
        limit=50,
        sort={"created_at": -1},
    )
    return tasks, runs


async def build_memory_context(
    patient_id: str,
    professional_id: str,
    clinic_id: str,
    current_run_id: Optional[str] = None
) -> Dict[str, Any]:
    try:
        memory_source = "native_adapter"
        task_docs: List[Dict[str, Any]] = []
        run_docs: List[Dict[str, Any]] = []

        if settings.mongodb_mcp_enabled and settings.state_backend == "mongodb":
            try:
                task_docs, run_docs = await _fetch_records_mcp(patient_id)
                memory_source = "official_mongodb_mcp_server"
            except Exception as e:
                logger.warning(f"Official MongoDB MCP read failed, falling back to native adapter: {e}")
                task_docs, run_docs = await _fetch_records_native(patient_id)
                memory_source = "native_adapter_fallback"
        else:
            task_docs, run_docs = await _fetch_records_native(patient_id)

        # 1. Filter tasks:
        # - exclude current run tasks
        # - prefer not done/rejected (i.e. proposed, approved, in_progress, blocked)
        # - limit to latest 10
        valid_tasks = []
        for t in task_docs:
            if current_run_id and t.get("agent_run_id") == current_run_id:
                continue
            if t.get("status") not in ["done", "rejected"]:
                valid_tasks.append(t)

        # sort by created_at descending (ISO strings sort chronologically)
        valid_tasks.sort(key=lambda x: x.get("created_at") or "", reverse=True)
        recent_tasks = valid_tasks[:10]

        items = []
        for t in recent_tasks:
            items.append({
                "task_id": t.get("task_id"),
                "title": t.get("title"),
                "status": t.get("status"),
                "created_at": t.get("created_at"),
            })

        # 2. Fetch past runs to extract preferences/facts
        facts = []
        for r in run_docs:
            if current_run_id and r.get("run_id") == current_run_id:
                continue

            result = r.get("result") or {}
            for fact in result.get("memory_facts") or []:
                # Only include compact administrative facts, exclude large text blobs
                fact_lower = str(fact).lower()
                if any(kw in fact_lower for kw in MEMORY_FACT_KEYWORDS):
                    if fact not in facts:
                        facts.append(fact)

        # Limit facts to latest 5 to keep context compact
        facts = facts[:5]
        for f in facts:
            items.append({
                "type": "patient_preference_or_fact",
                "fact": f
            })

        if not items:
            return {
                "memory_found": False,
                "items": [],
                "memory_source": memory_source,
                "summary": "No previous operational memory found for this synthetic patient."
            }

        return {
            "memory_found": True,
            "items": items,
            "memory_source": memory_source,
            "summary": "Existing operational memory found for this synthetic patient."
        }
    except Exception as e:
        logger.error(f"Failed to build memory context: {e}")
        # If memory builder fails, do not crash
        return {
            "memory_found": False,
            "items": [],
            "memory_source": "error",
            "summary": "No previous operational memory found for this synthetic patient.",
            "error": str(e)
        }
