from datetime import datetime, timezone

class Stats:
    def __init__(self):
        self.received = 0
        self.duplicates = 0
        self.start_time = datetime.now(timezone.utc)

    def increment_received(self):
        self.received += 1

    def increment_duplicate(self):
        self.duplicates += 1

    def to_dict(self):
        uptime = (datetime.now(timezone.utc) - self.start_time).total_seconds()
        return {
            "received": self.received,
            "duplicate_dropped": self.duplicates,
            "uptime": uptime
        }
