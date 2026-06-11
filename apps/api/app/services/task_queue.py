from fastapi import BackgroundTasks
from app.services.agent_run_simulator import simulate_agent_run


def enqueue_agent_run(run_id: str, background_tasks: BackgroundTasks):
    """Dispatch an agent run to the background processing queue.

    Uses FastAPI BackgroundTasks for in-process async execution.
    In a production deployment this would dispatch to Google Cloud Tasks
    targeting the dedicated Worker service.
    """
    background_tasks.add_task(simulate_agent_run, run_id)
