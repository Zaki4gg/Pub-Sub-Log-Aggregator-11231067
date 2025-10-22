import sys, os, time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from fastapi.testclient import TestClient
from src.main import app, dedup_store

client = TestClient(app)

def test_batch_publish_performance():
    dedup_store.clear_all()
    events = [
        {
            "topic": "stress.topic",
            "event_id": f"evt{i}",
            "timestamp": "2025-10-21T10:00:00Z",
            "source": "stress_test",
            "payload": {"num": i}
        }
        for i in range(100)
    ]
    res = client.post("/publish", json=events)
    assert res.status_code == 200
    time.sleep(0.5)
    stats = client.get("/stats").json()
    assert stats["received"] >= 100
