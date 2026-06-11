import motor.motor_asyncio
import pymongo
from app.config import settings

client = None
db = None

async def connect_to_mongo():
    global client, db
    if settings.state_backend != "mongodb":
        return
        
    try:
        client = motor.motor_asyncio.AsyncIOMotorClient(
            settings.mongodb_uri,
            serverSelectionTimeoutMS=settings.mongodb_connect_timeout_ms,
            appname="myukura-careops-memory-agent"
        )
        # Ensure connection works
        await client.server_info()
        db = client[settings.mongodb_database]
        
        # Ensure Indexes
        await ensure_indexes()
        
    except Exception as e:
        # We must throw structured errors if mongo fails when backend is mongodb
        raise Exception(f"MONGODB_CONNECTION_ERROR: Failed to connect to MongoDB Atlas. {str(e)}")

async def close_mongo_connection():
    global client
    if client is not None:
        client.close()

async def ensure_indexes():
    if db is None:
        return
        
    # Agent Runs
    await db["agent_runs"].create_index([("run_id", 1)], unique=True, background=True)
    await db["agent_runs"].create_index([("status", 1), ("created_at", 1)], background=True)
    await db["agent_runs"].create_index([("created_at", -1)], background=True)
    
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
