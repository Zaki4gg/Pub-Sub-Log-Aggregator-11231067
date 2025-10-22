import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from src.dedup_store import DedupStore

def test_persistence_across_restart():
    db_path = "test_persist.db"
    if os.path.exists(db_path):
        os.remove(db_path)

    store = DedupStore(db_path)
    store.add("topicX", "id123")

    # simulasi restart
    store2 = DedupStore(db_path)
    assert store2.is_duplicate("topicX", "id123")
