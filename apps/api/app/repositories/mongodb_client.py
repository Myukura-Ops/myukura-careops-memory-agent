"""MongoDB connection manager with retry logic and connection pooling.

Handles initial connection with exponential backoff for resilience
against transient Atlas outages. Configures production-grade pool
sizing, timeouts, and index creation.
"""
import asyncio
import logging

import motor.motor_asyncio
import pymongo
from app.config import settings

logger = logging.getLogger(__name__)

client = None
db = None

_MAX_CONNECT_RETRIES = 3
_BACKOFF_SECONDS = [1, 2, 4]


async def connect_to_mongo():
    """Connect to MongoDB Atlas with retry and exponential backoff.

    Retries up to 3 times (1s, 2s, 4s) before raising a fatal error.
    Configures connection pooling, timeouts, and automatic retries
    for reads and writes.
    """
    global client, db
    if settings.state_backend != "mongodb":
        logger.info("State backend is '%s'; skipping MongoDB connection.", settings.state_backend)
        return

    last_error = None
    for attempt in range(_MAX_CONNECT_RETRIES):
        try:
            client = motor.motor_asyncio.AsyncIOMotorClient(
                settings.mongodb_uri,
                serverSelectionTimeoutMS=settings.mongodb_connect_timeout_ms,
                connectTimeoutMS=settings.mongodb_connect_timeout_ms,
                socketTimeoutMS=30_000,
                maxPoolSize=20,
                minPoolSize=1,
                retryWrites=True,
                retryReads=True,
                appname=settings.mongodb_app_name,
            )
            await client.server_info()
            db = client[settings.mongodb_database]
            await ensure_indexes()
            logger.info("Connected to MongoDB Atlas (attempt %d/%d).", attempt + 1, _MAX_CONNECT_RETRIES)
            return
        except Exception as e:
            last_error = e
            if attempt < _MAX_CONNECT_RETRIES - 1:
                wait = _BACKOFF_SECONDS[attempt]
                logger.warning(
                    "MongoDB connection attempt %d/%d failed: %s. Retrying in %ds...",
                    attempt + 1, _MAX_CONNECT_RETRIES, e, wait,
                )
                await asyncio.sleep(wait)
            else:
                logger.error(
                    "MongoDB connection failed after %d attempts: %s",
                    _MAX_CONNECT_RETRIES, e,
                )

    raise Exception(
        f"MONGODB_CONNECTION_ERROR: Failed to connect to MongoDB Atlas "
        f"after {_MAX_CONNECT_RETRIES} attempts. Last error: {last_error}"
    )


async def close_mongo_connection():
    global client
    if client is not None:
        client.close()
        logger.info("MongoDB connection closed.")


async def ensure_indexes():
    if db is None:
        return

    # Agent Runs
    await db["agent_runs"].create_index([("run_id", 1)], unique=True, background=True)
    await db["agent_runs"].create_index([("status", 1), ("created_at", 1)], background=True)
    await db["agent_runs"].create_index([("created_at", -1)], background=True)
    await db["agent_runs"].create_index([("patient_id", 1), ("created_at", -1)], background=True)

    # Source Notes
    await db["source_notes"].create_index([("patient_id", 1), ("created_at", 1)], background=True)
    await db["source_notes"].create_index([("agent_run_id", 1)], background=True)

    # Audit Logs
    await db["agent_audit_logs"].create_index([("run_id", 1), ("timestamp", 1)], background=True)
    await db["agent_audit_logs"].create_index([("event_type", 1), ("timestamp", 1)], background=True)

    # Tasks
    await db["careops_tasks"].create_index([("task_id", 1)], unique=True, background=True)
    await db["careops_tasks"].create_index([("clinic_id", 1), ("status", 1), ("priority", 1)], background=True)
    await db["careops_tasks"].create_index([("patient_id", 1), ("status", 1)], background=True)
    await db["careops_tasks"].create_index([("agent_run_id", 1)], background=True)

    # Task Status History
    await db["task_status_history"].create_index([("task_id", 1), ("created_at", 1)], background=True)

    # Demographics
    await db["patients_demo"].create_index([("clinic_id", 1)], background=True)
    await db["professional_preferences"].create_index([("professional_id", 1), ("clinic_id", 1)], background=True)

    # Partner Outbox
    await db["partner_outbox"].create_index([("run_id", 1)], background=True)
    await db["partner_outbox"].create_index([("status", 1), ("created_at", 1)], background=True)

    # MCP Tool Calls
    await db["mcp_tool_calls"].create_index([("run_id", 1)], background=True)
