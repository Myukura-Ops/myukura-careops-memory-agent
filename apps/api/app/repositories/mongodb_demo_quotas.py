import logging
from datetime import datetime, timezone
from typing import Optional
from fastapi import HTTPException

from app.config import settings
from app.repositories import mongodb_client

logger = logging.getLogger(__name__)

COLLECTION_NAME = "demo_quotas"

async def check_and_increment_quota(quota_type: str, max_limit: int) -> bool:
    """
    Increments the quota counter for the given type for the current UTC day.
    Raises HTTPException 429 if the quota is exceeded or fails.
    If internal MongoDB error occurs, fails closed to prevent abuse.
    """
    if not settings.demo_quota_enabled:
        return True

    if mongodb_client.db is None:
        logger.warning(f"MongoDB not connected, but demo quota is enabled. Failing closed for {quota_type}.")
        raise HTTPException(
            status_code=503,
            detail="Service unavailable. Database connection failed."
        )

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    doc_id = f"{quota_type}_{today}"

    try:
        # We use return_document=AFTER to get the updated count.
        import pymongo
        result = await mongodb_client.db[COLLECTION_NAME].find_one_and_update(
            {"_id": doc_id},
            {"$inc": {"count": 1}, "$setOnInsert": {"date": today, "type": quota_type}},
            upsert=True,
            return_document=pymongo.ReturnDocument.AFTER
        )
        
        if result and result.get("count", 0) > max_limit:
            # We incremented but it's over the limit.
            logger.warning(f"Devpost demo quota exceeded for {quota_type}. Limit: {max_limit}")
            raise HTTPException(
                status_code=429,
                detail="Devpost demo quota exceeded. Please contact the team to refresh the judging quota."
            )
        return True
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking demo quota for {quota_type}: {e}")
        # Fail closed on write-heavy or Gemini endpoints
        raise HTTPException(
            status_code=503,
            detail="Service unavailable. Failed to verify quota."
        )

async def check_run_quota():
    await check_and_increment_quota("agent_runs", settings.max_demo_runs_per_day)

async def check_gemini_quota():
    await check_and_increment_quota("gemini_runs", settings.max_demo_gemini_runs_per_day)

async def check_partner_worker_quota():
    await check_and_increment_quota("partner_worker", settings.max_demo_partner_worker_calls_per_day)

async def check_seed_quota():
    await check_and_increment_quota("seed_calls", settings.max_demo_seed_calls_per_day)

async def check_task_mutation_quota():
    await check_and_increment_quota("task_mutations", settings.max_demo_task_mutations_per_day)
