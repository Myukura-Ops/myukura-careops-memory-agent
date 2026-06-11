import logging
from typing import Dict, Any, Optional

from app.config import settings
from app.models.partner_outbox import PartnerOutbox
from app.repositories.repository_factory import get_partner_outbox_repo

logger = logging.getLogger(__name__)

async def process_single_partner_outbox_item(item: PartnerOutbox) -> dict:
    repo = get_partner_outbox_repo()
    
    if item.partner == "arize":
        if not getattr(settings, "arize_export_enabled", False):
            # Dry run / disabled branch
            await repo.update_partner_outbox_status(
                outbox_id=item.outbox_id,
                status="skipped",
                last_error="external_export_disabled"
            )
            return {"status": "skipped", "reason": "external_export_disabled"}
        else:
            # Enabled but no real implementation yet
            await repo.update_partner_outbox_status(
                outbox_id=item.outbox_id,
                status="failed",
                last_error="arize_export_not_implemented"
            )
            return {"status": "failed", "reason": "arize_export_not_implemented"}
            
    elif item.partner == "elastic":
        if not getattr(settings, "elastic_export_enabled", False):
            await repo.update_partner_outbox_status(
                outbox_id=item.outbox_id,
                status="skipped",
                last_error="external_indexing_disabled"
            )
            return {"status": "skipped", "reason": "external_indexing_disabled"}
        else:
            await repo.update_partner_outbox_status(
                outbox_id=item.outbox_id,
                status="failed",
                last_error="elastic_export_not_implemented"
            )
            return {"status": "failed", "reason": "elastic_export_not_implemented"}
            
    else:
        # Unknown partner
        await repo.update_partner_outbox_status(
            outbox_id=item.outbox_id,
            status="failed",
            last_error="unknown_partner"
        )
        return {"status": "failed", "reason": "unknown_partner"}


async def process_partner_outbox_once(*, partner: Optional[str] = None, limit: int = 20) -> Dict[str, Any]:
    repo = get_partner_outbox_repo()
    items = await repo.list_pending_partner_outbox(partner=partner, limit=limit)
    
    summary = {
        "processed": 0,
        "skipped": 0,
        "failed": 0,
        "sent": 0,
        "external_exports_active": False,
        "items": []
    }
    
    if not items:
        return summary
        
    for item in items:
        result = await process_single_partner_outbox_item(item)
        
        # Build safe summary item representation
        item_summary = {
            "outbox_id": item.outbox_id,
            "partner": item.partner,
            "payload_type": item.payload_type,
            "status": result["status"],
            "reason": result["reason"]
        }
        summary["items"].append(item_summary)
        summary["processed"] += 1
        
        if result["status"] == "skipped":
            summary["skipped"] += 1
        elif result["status"] == "failed":
            summary["failed"] += 1
        elif result["status"] == "sent":
            summary["sent"] += 1
            
    return summary
