import asyncio

async def seed_data():
    print("Seeding synthetic demo data...")
    # TODO in Phase 2: Connect to MongoDB Atlas and insert clinics, patients_demo, source_notes
    print("Done. Phase 0: database not connected.")

if __name__ == "__main__":
    asyncio.run(seed_data())
