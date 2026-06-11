from datetime import datetime, timezone
from app.repositories import mongodb_client

async def get_activity_stats():
    if mongodb_client.db is None:
        return {
            "backend": "memory",
            "latest_run_id": None,
            "collections_touched": [],
            "write_counts": 0,
            "latest_document_ids": {},
            "refreshed_at": datetime.now(timezone.utc).isoformat()
        }
        
    collections = await mongodb_client.db.list_collection_names()
    
    # Rough estimate of write counts by just counting documents for the demo
    write_counts = {}
    total_writes = 0
    latest_docs = {}
    
    # Let's get the latest run id
    latest_run = await mongodb_client.db["agent_runs"].find_one({}, sort=[("created_at", -1)])
    latest_run_id = latest_run["run_id"] if latest_run else None
    
    for coll in ["clinics", "patients_demo", "professional_preferences", "source_notes", "agent_runs", "careops_tasks", "agent_audit_logs", "task_status_history", "mcp_tool_calls"]:
        if coll in collections:
            count = await mongodb_client.db[coll].count_documents({})
            write_counts[coll] = count
            total_writes += count
            latest = await mongodb_client.db[coll].find_one({}, sort=[("_id", -1)])
            if latest:
                latest_docs[coll] = str(latest["_id"])
                
    return {
        "backend": "mongodb",
        "latest_run_id": latest_run_id,
        "collections_touched": collections,
        "write_counts": write_counts,
        "total_writes": total_writes,
        "latest_document_ids": latest_docs,
        "refreshed_at": datetime.now(timezone.utc).isoformat()
    }
