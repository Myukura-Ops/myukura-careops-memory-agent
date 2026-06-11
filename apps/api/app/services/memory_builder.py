from typing import Dict, Any, Optional
from app.repositories.repository_factory import get_tasks_repo, get_agent_runs_repo

async def build_memory_context(
    patient_id: str,
    professional_id: str,
    clinic_id: str,
    current_run_id: Optional[str] = None
) -> Dict[str, Any]:
    try:
        tasks_repo = get_tasks_repo()
        runs_repo = get_agent_runs_repo()
        
        # 1. Fetch synthetic operational memory (tasks)
        all_tasks = await tasks_repo.get_tasks_by_patient(patient_id)
        
        # 2. Filter tasks:
        # - exclude current run tasks
        # - prefer not done/rejected (i.e. proposed, approved, in_progress, blocked)
        # - limit to latest 10
        valid_tasks = []
        for t in all_tasks:
            if current_run_id and t.agent_run_id == current_run_id:
                continue
            if t.status not in ["done", "rejected"]:
                valid_tasks.append(t)
        
        # sort by created_at descending (should already be, but ensure it)
        valid_tasks.sort(key=lambda x: x.created_at, reverse=True)
        recent_tasks = valid_tasks[:10]
        
        items = []
        for t in recent_tasks:
            items.append({
                "task_id": t.task_id,
                "title": t.title,
                "status": t.status,
                "created_at": t.created_at.isoformat() if t.created_at else None,
            })

        # 3. Fetch past runs to extract preferences/facts
        all_runs = await runs_repo.get_runs_by_patient(patient_id)
        facts = []
        for r in all_runs:
            if current_run_id and r.run_id == current_run_id:
                continue
            
            if r.result and "memory_facts" in r.result and r.result["memory_facts"]:
                # Only include compact facts, exclude large text blobs
                for fact in r.result["memory_facts"]:
                    # check if the fact relates to administrative, communication, portal, forms, insurance
                    fact_lower = fact.lower()
                    if any(kw in fact_lower for kw in ["language", "communication", "portal", "form", "consent", "insurance", "preference"]):
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
                "summary": "No previous operational memory found for this synthetic patient."
            }
            
        return {
            "memory_found": True,
            "items": items,
            "summary": "Existing operational memory found for this synthetic patient."
        }
    except Exception as e:
        import logging
        logging.error(f"Failed to build memory context: {e}")
        # If memory builder fails, do not crash
        return {
            "memory_found": False,
            "items": [],
            "summary": "No previous operational memory found for this synthetic patient.",
            "error": str(e)
        }
