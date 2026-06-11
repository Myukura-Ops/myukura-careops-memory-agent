from typing import Optional
from app.models.notes import SourceNote
from app.repositories import mongodb_client

async def create_source_note(note: SourceNote) -> SourceNote:
    note_dict = note.model_dump(by_alias=True, exclude_none=True)
    await mongodb_client.db["source_notes"].insert_one(note_dict)
    return note

async def get_source_note(note_id: str) -> Optional[SourceNote]:
    doc = await mongodb_client.db["source_notes"].find_one({"note_id": note_id})
    if doc:
        doc.pop("_id", None)
        return SourceNote(**doc)
    return None
