from fastapi import BackgroundTasks
from app.services.agent_run_simulator import simulate_agent_run

# Phase 1 mock queue. Replace with Cloud Tasks in a later phase.

def enqueue_agent_run(run_id: str, background_tasks: BackgroundTasks):
    """
    Dispatches the agent run to a queue.
    In Phase 1, it adds an asyncio task to the FastAPI background tasks.
    In Phase 2/3, this will send a Cloud Task to invoke the Worker service.
    """
    background_tasks.add_task(simulate_agent_run, run_id)
