from app.config import settings

def get_agent_runs_repo():
    if settings.state_backend == "mongodb":
        from app.repositories import mongodb_agent_runs
        return mongodb_agent_runs
    else:
        # Phase 1 Fallback / Demo only
        from app.repositories import in_memory_agent_runs
        return in_memory_agent_runs

# Source notes and tasks use MongoDB in production. When STATE_BACKEND=memory,
# an in-memory fallback is used for local development and offline testing.
class InMemoryFallbackRepo:
    def __init__(self):
        self._tasks = {}
        self._notes = {}

    async def create_source_note(self, note):
        key = getattr(note, 'note_id', None) or note.get('note_id') if isinstance(note, dict) else getattr(note, 'id', None)
        self._notes[key] = note
        return note

    async def get_source_note(self, note_id): 
        return self._notes.get(note_id)

    async def create_task(self, task):
        self._tasks[task.task_id] = task
        return task

    async def get_task(self, task_id): 
        return self._tasks.get(task_id)

    async def list_tasks(self, clinic_id=None): 
        return list(self._tasks.values())

    async def get_tasks_by_patient(self, patient_id): 
        return [t for t in self._tasks.values() if t.patient_id == patient_id]

    async def get_runs_by_patient(self, patient_id): 
        from app.repositories import in_memory_agent_runs
        return await in_memory_agent_runs.get_runs_by_patient(patient_id)

    async def update_task_status(self, task_id, status, by, reason): 
        if task_id in self._tasks:
            self._tasks[task_id].status = status
            return self._tasks[task_id]
        return None

_in_memory_fallback_instance = InMemoryFallbackRepo()
    
def get_source_notes_repo():
    if settings.state_backend == "mongodb":
        from app.repositories import mongodb_source_notes
        return mongodb_source_notes
    return _in_memory_fallback_instance

def get_tasks_repo():
    if settings.state_backend == "mongodb":
        from app.repositories import mongodb_tasks
        return mongodb_tasks
    return _mock_repo_instance

def get_mcp_tool_calls_repo():
    if settings.state_backend == "mongodb":
        from app.repositories.mongodb_mcp_tool_calls import MongoDBMCPToolCallsRepository
        return MongoDBMCPToolCallsRepository()
    from app.repositories.in_memory_mcp_tool_calls import InMemoryMCPToolCallsRepository
    return InMemoryMCPToolCallsRepository()

_in_memory_partner_outbox_instance = None

def get_partner_outbox_repo():
    if settings.state_backend == "mongodb":
        from app.repositories.mongodb_partner_outbox import MongoDBPartnerOutboxRepository
        return MongoDBPartnerOutboxRepository()
    global _in_memory_partner_outbox_instance
    if _in_memory_partner_outbox_instance is None:
        from app.repositories.in_memory_partner_outbox import InMemoryPartnerOutboxRepository
        _in_memory_partner_outbox_instance = InMemoryPartnerOutboxRepository()
    return _in_memory_partner_outbox_instance
