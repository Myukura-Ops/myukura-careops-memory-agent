from datetime import datetime, timezone
from typing import List, Optional
from app.models.partner_outbox import PartnerOutbox
from app.repositories import mongodb_client

COLLECTION_NAME = "partner_outbox"

class MongoDBPartnerOutboxRepository:
    def _to_model(self, doc: dict) -> PartnerOutbox:
        if not doc:
            return None
        doc.pop("_id", None)
        return PartnerOutbox(**doc)

    async def create_partner_outbox_item(self, item: PartnerOutbox) -> PartnerOutbox:
        if mongodb_client.db is None:
            return item
        doc = item.model_dump()
        try:
            await mongodb_client.db[COLLECTION_NAME].insert_one(doc)
        except Exception:
            pass # Best effort creation
        return item

    async def create_partner_outbox_items(self, items: list[PartnerOutbox]) -> list[PartnerOutbox]:
        if mongodb_client.db is None or not items:
            return items
        docs = [item.model_dump() for item in items]
        try:
            await mongodb_client.db[COLLECTION_NAME].insert_many(docs, ordered=False)
        except Exception:
            pass
        return items

    async def get_partner_outbox_by_run(self, run_id: str) -> list[PartnerOutbox]:
        if mongodb_client.db is None:
            return []
        try:
            cursor = mongodb_client.db[COLLECTION_NAME].find({"run_id": run_id})
            docs = await cursor.to_list(length=100)
            return [self._to_model(doc) for doc in docs]
        except Exception:
            return []

    async def list_pending_partner_outbox(self, partner: Optional[str] = None, limit: int = 20) -> list[PartnerOutbox]:
        if mongodb_client.db is None:
            return []
        try:
            query = {"status": "pending"}
            if partner:
                query["partner"] = partner
            cursor = mongodb_client.db[COLLECTION_NAME].find(query).sort("created_at", 1).limit(limit)
            docs = await cursor.to_list(length=limit)
            return [self._to_model(doc) for doc in docs]
        except Exception:
            return []

    async def update_partner_outbox_status(
        self,
        outbox_id: str,
        status: str,
        last_error: Optional[str] = None,
        sent_at: Optional[datetime] = None
    ) -> Optional[PartnerOutbox]:
        if mongodb_client.db is None:
            return None
            
        update_fields = {
            "status": status,
            "updated_at": datetime.now(timezone.utc)
        }
        if last_error is not None:
            update_fields["last_error"] = last_error[:300]
        if sent_at is not None:
            update_fields["sent_at"] = sent_at
            
        try:
            doc = await mongodb_client.db[COLLECTION_NAME].find_one_and_update(
                {"outbox_id": outbox_id},
                {"$set": update_fields},
                return_document=True
            )
            return self._to_model(doc) if doc else None
        except Exception:
            return None

    async def increment_partner_outbox_attempt(
        self,
        outbox_id: str,
        last_error: Optional[str] = None,
        next_attempt_at: Optional[datetime] = None
    ) -> Optional[PartnerOutbox]:
        if mongodb_client.db is None:
            return None
            
        update_fields = {
            "updated_at": datetime.now(timezone.utc)
        }
        if last_error is not None:
            update_fields["last_error"] = last_error[:300]
        if next_attempt_at is not None:
            update_fields["next_attempt_at"] = next_attempt_at
            
        try:
            doc = await mongodb_client.db[COLLECTION_NAME].find_one_and_update(
                {"outbox_id": outbox_id},
                {"$inc": {"attempt_count": 1}, "$set": update_fields},
                return_document=True
            )
            return self._to_model(doc) if doc else None
        except Exception:
            return None
