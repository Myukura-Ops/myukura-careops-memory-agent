import logging
from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.config import settings
from app.routes import agent_runs, tasks, demo, mcp_tools
from app.repositories import mongodb_client
from app.security.demo_access import require_demo_access

logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])


def _rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Return a structured JSON response when rate limit is exceeded."""
    return JSONResponse(
        status_code=429,
        content={
            "error_type": "RATE_LIMIT_EXCEEDED",
            "message": f"Rate limit exceeded: {exc.detail}",
            "suggestion": "Wait before retrying. The demo allows 100 requests per minute.",
            "retryable": True,
            "status": "failed",
        },
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: connect to MongoDB on startup, disconnect on shutdown."""
    await mongodb_client.connect_to_mongo()
    yield
    await mongodb_client.close_mongo_connection()


app = FastAPI(
    title=settings.project_name,
    version="1.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Protected routers — all require demo access code
app.include_router(agent_runs.router, dependencies=[Depends(require_demo_access)])
app.include_router(tasks.router, dependencies=[Depends(require_demo_access)])
app.include_router(demo.router, dependencies=[Depends(require_demo_access)])
app.include_router(mcp_tools.router, dependencies=[Depends(require_demo_access)])


@app.get("/health")
async def health_check():
    """Unauthenticated health probe for Cloud Run and load balancers."""
    return {
        "status": "healthy",
        "app_env": settings.app_env,
        "runtime": settings.runtime,
        "state_backend": settings.state_backend,
        "demo_mode": settings.demo_mode,
        "gemini_enabled": settings.gemini_enabled,
        "observability_enabled": settings.observability_enabled,
    }


@app.get("/version", dependencies=[Depends(require_demo_access)])
async def get_version():
    return {"phase": settings.phase, "project": settings.project_name}


@app.get("/architecture-summary", dependencies=[Depends(require_demo_access)])
async def architecture_summary():
    return {
        "architecture": [
            "Frontend (React) -> Cloud Run API",
            "Cloud Run API -> Cloud Tasks -> Cloud Run Worker",
            "Cloud Run Worker -> Gemini / MongoDB MCP",
            "State -> MongoDB Atlas",
        ],
        "safety": "Synthetic demo only. No diagnosis. Human-in-the-loop required.",
    }
