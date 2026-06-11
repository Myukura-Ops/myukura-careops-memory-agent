from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.repositories import mongodb_seed, mongodb_activity

router = APIRouter(tags=["demo"])

@router.post("/demo/seed")
async def seed_data():
    try:
        res = await mongodb_seed.seed_demo_data()
        return res
    except Exception as e:
        return JSONResponse(status_code=500, content={"error_type": "SEED_DATA_ERROR", "message": str(e), "suggestion": "Ensure MongoDB is connected.", "retryable": True, "status": "failed"})

@router.get("/mongodb/activity")
async def get_activity():
    return await mongodb_activity.get_activity_stats()

@router.post("/demo/partner-outbox/process-once")
async def process_partner_outbox():
    from app.services.partner_export_worker import process_partner_outbox_once
    try:
        summary = await process_partner_outbox_once(limit=20)
        return summary
    except Exception as e:
        return JSONResponse(status_code=500, content={"error_type": "PARTNER_OUTBOX_ERROR", "message": str(e)[:300], "suggestion": "Check backend logs.", "retryable": True, "status": "failed"})
