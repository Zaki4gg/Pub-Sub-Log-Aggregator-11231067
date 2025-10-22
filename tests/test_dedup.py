import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from src.dedup_store import DedupStore

def test_deduplication_logic():
    db = DedupStore("test_dedup.db")
    db.add("topic1", "id1")
    assert db.is_duplicate("topic1", "id1") is True
    assert db.is_duplicate("topic1", "id2") is False
