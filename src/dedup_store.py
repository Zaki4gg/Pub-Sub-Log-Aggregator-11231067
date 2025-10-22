import sqlite3
from pathlib import Path

class DedupStore:
    def __init__(self, db_path: str = "dedup_store.db"):
        self.db_path = Path(db_path)
        self._ensure_table()

    def _ensure_table(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS dedup (
                    topic TEXT NOT NULL,
                    event_id TEXT NOT NULL,
                    PRIMARY KEY (topic, event_id)
                )
            """)
            conn.commit()

    def is_duplicate(self, topic: str, event_id: str) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT 1 FROM dedup WHERE topic=? AND event_id=?",
                (topic, event_id)
            )
            return cursor.fetchone() is not None

    def add(self, topic: str, event_id: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR IGNORE INTO dedup (topic, event_id) VALUES (?, ?)",
                (topic, event_id)
            )
            conn.commit()

    def clear_all(self):
        """Hapus semua data (khusus untuk unit test)."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM dedup")
            conn.commit()
