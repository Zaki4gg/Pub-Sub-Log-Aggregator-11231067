import sys, os, time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from fastapi.testclient import TestClient
from src.main import app, dedup_store

client = TestClient(app)

def test_publish_and_stats():
    dedup_store.clear_all()  # reset DB sebelum test
    event = {
        "topic": "test.topic",
        "event_id": "evt001",
        "timestamp": "2025-10-21T10:00:00Z",
        "source": "unit_test",
        "payload": {"msg": "hello world"}
    }
    res = client.post("/publish", json=event)
    assert res.status_code == 200
    time.sleep(0.2)
    stats = client.get("/stats").json()
    assert "received" in stats
    assert stats["received"] >= 1
