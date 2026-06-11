from datetime import datetime, timezone
from typing import List, Optional
from app.models.partner_outbox import PartnerOutbox

class InMemoryPartnerOutboxRepository:
    def __init__(self):
        self._items = {}

    async def create_partner_outbox_item(self, item: PartnerOutbox) -> PartnerOutbox:
        self._items[item.outbox_id] = item
        return item

    async def create_partner_outbox_items(self, items: list[PartnerOutbox]) -> list[PartnerOutbox]:
        for item in items:
            self._items[item.outbox_id] = item
        return items

    async def get_partner_outbox_by_run(self, run_id: str) -> list[PartnerOutbox]:
        results = [item for item in self._items.values() if item.run_id == run_id]
        return results

    async def list_pending_partner_outbox(self, partner: Optional[str] = None, limit: int = 20) -> list[PartnerOutbox]:
        results = [item for item in self._items.values() if item.status == "pending"]
        if partner:
            results = [item for item in results if item.partner == partner]
        results.sort(key=lambda x: x.created_at)
        return results[:limit]

    async def update_partner_outbox_status(
        self,
        outbox_id: str,
        status: str,
        last_error: Optional[str] = None,
        sent_at: Optional[datetime] = None
    ) -> Optional[PartnerOutbox]:
        if outbox_id not in self._items:
            return None
        item = self._items[outbox_id]
        item.status = status
        item.updated_at = datetime.now(timezone.utc)
        if last_error is not None:
            item.last_error = last_error[:300]
        if sent_at is not None:
            item.sent_at = sent_at
        return item

    async def increment_partner_outbox_attempt(
        self,
        outbox_id: str,
        last_error: Optional[str] = None,
        next_attempt_at: Optional[datetime] = None
    ) -> Optional[PartnerOutbox]:
        if outbox_id not in self._items:
            return None
        item = self._items[outbox_id]
        item.attempt_count += 1
        item.updated_at = datetime.now(timezone.utc)
        if last_error is not None:
            item.last_error = last_error[:300]
        if next_attempt_at is not None:
            item.next_attempt_at = next_attempt_at
        return item
