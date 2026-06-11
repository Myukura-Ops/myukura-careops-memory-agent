from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.routes import agent_runs, tasks, demo, mcp_tools
from app.repositories import mongodb_client
from app.security.demo_access import require_demo_access

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Connect to MongoDB if configured
    await mongodb_client.connect_to_mongo()
    yield
    # Close connection on shutdown
    await mongodb_client.close_mongo_connection()

app = FastAPI(
    title=settings.project_name,
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agent_runs.router, dependencies=[Depends(require_demo_access)])
app.include_router(tasks.router, dependencies=[Depends(require_demo_access)])
app.include_router(demo.router, dependencies=[Depends(require_demo_access)])
app.include_router(mcp_tools.router, dependencies=[Depends(require_demo_access)])


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app_env": settings.app_env,
        "runtime": settings.runtime,
        "state_backend": settings.state_backend,
        "demo_mode": settings.demo_mode,
        "gemini_enabled": settings.gemini_enabled,
        "observability_enabled": settings.observability_enabled,
        "mongodb_status": "not_checked"
    }

@app.get("/version")
async def get_version():
    return {"phase": settings.phase, "project": settings.project_name}

@app.get("/architecture-summary")
async def architecture_summary():
    return {
        "architecture": [
            "Frontend (React) -> Cloud Run API",
            "Cloud Run API -> Cloud Tasks -> Cloud Run Worker",
            "Cloud Run Worker -> Gemini / MongoDB MCP",
            "State -> MongoDB Atlas"
        ],
        "safety": "Synthetic demo only. No diagnosis. Human-in-the-loop required."
    }
