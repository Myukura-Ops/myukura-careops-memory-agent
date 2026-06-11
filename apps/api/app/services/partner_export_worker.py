import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Tuple

import httpx

from app.config import settings
from app.models.partner_outbox import PartnerOutbox
from app.repositories.repository_factory import get_partner_outbox_repo

logger = logging.getLogger(__name__)


async def _send_arize(item: PartnerOutbox) -> Tuple[str, str]:
    """Send an observability record to Arize. Returns (status, reason)."""
    if not settings.arize_endpoint or not settings.arize_api_key or not settings.arize_space_id:
        return "skipped", "arize_credentials_missing"

    headers = {
        "Authorization": f"Bearer {settings.arize_api_key}",
        "space_id": settings.arize_space_id,
        "Content-Type": "application/json",
    }
    body = {
        "project_name": settings.arize_project_name,
        "record_type": item.payload_type,
        "record": item.payload,
    }
    try:
        async with httpx.AsyncClient(timeout=settings.partner_export_timeout_seconds) as client:
            resp = await client.post(settings.arize_endpoint, json=body, headers=headers)
    except httpx.HTTPError as exc:
        return "retry", f"arize_transport_error:{type(exc).__name__}"

    if resp.status_code in (200, 201, 202):
        return "sent", f"arize_http_{resp.status_code}"
    if resp.status_code in (401, 403):
        return "failed", f"arize_auth_error_{resp.status_code}"
    return "retry", f"arize_http_{resp.status_code}"


async def _send_elastic(item: PartnerOutbox) -> Tuple[str, str]:
    """Index an audit document into Elasticsearch. Returns (status, reason)."""
    if not settings.elastic_endpoint or not settings.elastic_api_key:
        return "skipped", "elastic_credentials_missing"

    url = f"{settings.elastic_endpoint.rstrip('/')}/{settings.elastic_index}/_doc"
    headers = {
        "Authorization": f"ApiKey {settings.elastic_api_key}",
        "Content-Type": "application/json",
    }
    doc = {
        "outbox_id": item.outbox_id,
        "run_id": item.run_id,
        "payload_type": item.payload_type,
        "indexed_at": datetime.now(timezone.utc).isoformat(),
        **item.payload,
    }
    try:
        async with httpx.AsyncClient(timeout=settings.partner_export_timeout_seconds) as client:
            resp = await client.post(url, json=doc, headers=headers)
    except httpx.HTTPError as exc:
        return "retry", f"elastic_transport_error:{type(exc).__name__}"

    if resp.status_code in (200, 201):
        return "sent", f"elastic_http_{resp.status_code}"
    if resp.status_code in (401, 403):
        return "failed", f"elastic_auth_error_{resp.status_code}"
    return "retry", f"elastic_http_{resp.status_code}"


async def process_single_partner_outbox_item(item: PartnerOutbox) -> dict:
    repo = get_partner_outbox_repo()

    if item.partner == "arize":
        if not settings.arize_export_enabled:
            await repo.update_partner_outbox_status(
                outbox_id=item.outbox_id,
                status="skipped",
                last_error="external_export_disabled"
            )
            return {"status": "skipped", "reason": "external_export_disabled"}
        status, reason = await _send_arize(item)

    elif item.partner == "elastic":
        if not settings.elastic_export_enabled:
            await repo.update_partner_outbox_status(
                outbox_id=item.outbox_id,
                status="skipped",
                last_error="external_indexing_disabled"
            )
            return {"status": "skipped", "reason": "external_indexing_disabled"}
        status, reason = await _send_elastic(item)

    else:
        await repo.update_partner_outbox_status(
            outbox_id=item.outbox_id,
            status="failed",
            last_error="unknown_partner"
        )
        return {"status": "failed", "reason": "unknown_partner"}

    if status == "sent":
        await repo.update_partner_outbox_status(
            outbox_id=item.outbox_id,
            status="sent",
            last_error=None,
            sent_at=datetime.now(timezone.utc)
        )
        return {"status": "sent", "reason": reason}

    if status == "skipped":
        await repo.update_partner_outbox_status(
            outbox_id=item.outbox_id,
            status="skipped",
            last_error=reason
        )
        return {"status": "skipped", "reason": reason}

    if status == "retry":
        updated = await repo.increment_partner_outbox_attempt(
            outbox_id=item.outbox_id,
            last_error=reason
        )
        attempts = updated.attempt_count if updated else item.attempt_count + 1
        max_attempts = item.max_attempts or settings.partner_max_attempts
        if attempts >= max_attempts:
            await repo.update_partner_outbox_status(
                outbox_id=item.outbox_id,
                status="failed",
                last_error=f"max_attempts_exceeded:{reason}"
            )
            return {"status": "failed", "reason": f"max_attempts_exceeded:{reason}"}
        return {"status": "pending", "reason": reason}

    # status == "failed" (non-retryable, e.g. auth errors)
    await repo.update_partner_outbox_status(
        outbox_id=item.outbox_id,
        status="failed",
        last_error=reason
    )
    return {"status": "failed", "reason": reason}


async def process_partner_outbox_once(*, partner: Optional[str] = None, limit: int = 20) -> Dict[str, Any]:
    repo = get_partner_outbox_repo()
    items = await repo.list_pending_partner_outbox(partner=partner, limit=limit)

    summary = {
        "processed": 0,
        "skipped": 0,
        "failed": 0,
        "sent": 0,
        "retrying": 0,
        "external_exports_active": settings.arize_export_enabled or settings.elastic_export_enabled,
        "items": []
    }

    if not items:
        return summary

    for item in items:
        result = await process_single_partner_outbox_item(item)

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
        elif result["status"] == "pending":
            summary["retrying"] += 1

    return summary
