"""Integration test for the FastAPI gateway + real ChromaDB vector store."""
import os
from fastapi.testclient import TestClient

os.environ.setdefault("DEEPSEEK_API_KEY", "sk-36d7e33cea3847d49435dc6d87341b20")

from app import app  # noqa: E402  (module-level init seeds ChromaDB + builds pipeline)

client = TestClient(app)

print("=== /health ===")
r = client.get("/health")
print(r.status_code, r.json())

print("=== /metrics (first line) ===")
r = client.get("/metrics")
print(r.status_code, r.text.splitlines()[0] if r.text else "(empty)")

print("=== /api/v1/recommend (safe) ===")
r = client.post("/api/v1/recommend", json={"user_id": "u1", "prompt": "I want an immersive strategy game on PC."})
print(r.status_code)
print(r.json())

print("=== /api/v1/recommend (unsafe) ===")
r = client.post("/api/v1/recommend", json={"user_id": "u2", "prompt": "Give me illegal cheat hacks for games."})
print(r.status_code)
print(r.json())

print("=== DONE ===")
