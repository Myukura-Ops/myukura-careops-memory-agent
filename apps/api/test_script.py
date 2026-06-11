import json
from app.main import app
from fastapi.testclient import TestClient
import time
import os

os.environ["STATE_BACKEND"] = "memory"
os.environ["GEMINI_ENABLED"] = "false"

client = TestClient(app)

print("=== 1. Mock mode still works ===")
payload = {
  "clinic_id": "clinic_demo",
  "patient_id": "patient_demo",
  "professional_id": "prof_demo",
  "source_note": "Approved synthetic post-consultation note: schedule follow-up, prepare visit summary, check missing administrative form. No diagnosis or treatment changes.",
  "mode": "mock"
}
response = client.post("/agent-runs/", json=payload)
print("POST /agent-runs:", response.status_code, response.json())
if response.status_code == 200:
    run_id = response.json()["run_id"]
    
    get_resp = client.get(f"/agent-runs/{run_id}")
    print(f"GET /agent-runs/{run_id}:", get_resp.status_code, get_resp.json())
    
    events_resp = client.get(f"/agent-runs/{run_id}/events")
    print(f"GET /agent-runs/{run_id}/events:", events_resp.status_code, json.dumps(events_resp.json(), indent=2))
    
    tasks_resp = client.get(f"/tasks?clinic_id=clinic_demo")
    all_tasks = tasks_resp.json()
    run_tasks = [t for t in all_tasks if t.get("agent_run_id") == run_id]
    print(f"GET /tasks filtered by run_id:", json.dumps(run_tasks, indent=2))
    print("\n")


print("=== 2. Gemini disabled behavior ===")
payload_gemini = {
  "clinic_id": "clinic_demo",
  "patient_id": "patient_demo",
  "professional_id": "prof_demo",
  "source_note": "Approved synthetic post-consultation note...",
  "mode": "gemini"
}
response_gemini = client.post("/agent-runs/", json=payload_gemini)
print("POST /agent-runs with mode='gemini':", response_gemini.status_code, json.dumps(response_gemini.json(), indent=2))
print("\n")
