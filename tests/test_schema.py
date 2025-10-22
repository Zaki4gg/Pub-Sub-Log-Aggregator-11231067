import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_invalid_event_schema():
    bad_event = {
        "topic": "missing_event_id",
        "timestamp": "2025-10-21T10:00:00Z",
        "source": "test",
        "payload": {"msg": "bad data"}
    }
    res = client.post("/publish", json=bad_event)
    assert res.status_code == 422
