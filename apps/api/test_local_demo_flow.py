import asyncio
import httpx
import time

async def verify():
    async with httpx.AsyncClient() as client:
        print("1. Testing Health...")
        res = await client.get("http://localhost:8000/health")
        if res.status_code != 200:
            print("API not running. Please start uvicorn app.main:app")
            return
        print(res.json())
        
        print("\n2. Testing Seed Data...")
        res = await client.post("http://localhost:8000/demo/seed")
        print(res.status_code, res.json())

        print("\n3. Triggering Mock Run...")
        res = await client.post("http://localhost:8000/agent-runs/", json={
            "clinic_id": "clinic_demo",
            "patient_id": "patient_demo",
            "professional_id": "prof_demo",
            "source_note": "Approved synthetic post-consultation note.",
            "mode": "mock"
        })
        
        if res.status_code != 200:
            print("Agent run failed:", res.status_code, res.json())
            return
            
        data = res.json()
        run_id = data["run_id"]
        print(f"Run {run_id} started. Waiting 3 seconds...")
        await asyncio.sleep(3)

        print("\n4. Checking MongoDB Activity...")
        act_res = await client.get("http://localhost:8000/mongodb/activity")
        print(act_res.json())

if __name__ == "__main__":
    asyncio.run(verify())
