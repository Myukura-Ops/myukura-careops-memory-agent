from datetime import datetime, timezone
from app.repositories import mongodb_client

async def seed_demo_data():
    if mongodb_client.db is None:
        return {"status": "skipped", "message": "MongoDB not connected."}
        
    now = datetime.now(timezone.utc)
    
    # Clinics
    await mongodb_client.db["clinics"].update_one(
        {"clinic_id": "clinic_demo"},
        {"$setOnInsert": {
            "clinic_id": "clinic_demo",
            "name": "Demo Clinic",
            "mode": "synthetic_demo",
            "region": "US-West",
            "settings": {
                "require_human_approval": True,
                "allow_real_delivery": False,
                "default_language": "en"
            },
            "created_at": now,
            "updated_at": now
        }},
        upsert=True
    )
    
    # Patients Demo
    await mongodb_client.db["patients_demo"].update_one(
        {"patient_id": "patient_demo"},
        {"$setOnInsert": {
            "patient_id": "patient_demo",
            "clinic_id": "clinic_demo",
            "display_name": "Patient Demo A",
            "language": "en",
            "tags": ["demo", "synthetic"],
            "operational_context": "Routine follow-up patient.",
            "created_at": now,
            "updated_at": now
        }},
        upsert=True
    )
    
    # Professional Preferences
    await mongodb_client.db["professional_preferences"].update_one(
        {"professional_id": "prof_demo"},
        {"$setOnInsert": {
            "professional_id": "prof_demo",
            "clinic_id": "clinic_demo",
            "handoff_style": "bullet_points",
            "task_priority_rules": "strict",
            "language_preference": "en",
            "review_mode": "manual_only",
            "created_at": now,
            "updated_at": now
        }},
        upsert=True
    )
    
    return {"status": "success", "message": "Synthetic demo data seeded."}
