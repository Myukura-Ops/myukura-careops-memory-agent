from fastapi import FastAPI
from pydantic import BaseModel
from app.config import settings

class ProcessRunRequest(BaseModel):
    run_id: str

app = FastAPI(title=settings.project_name)

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "careops-worker"}

@app.post("/worker/process-run")
async def process_run(request: ProcessRunRequest):
    return {
        "status": "accepted",
        "run_id": request.run_id,
        "phase": settings.phase,
        "message": "Worker processing is simulated in Phase 1. Real Cloud Tasks integration comes later."
    }
