import asyncio
from src.models import Event

class Consumer:
    def __init__(self, dedup_store, stats):
        self.queue = asyncio.Queue()
        self.dedup_store = dedup_store
        self.stats = stats

    async def enqueue(self, event: Event):
        await self.queue.put(event)

    async def worker_once(self):
        """Proses satu event (untuk test atau sinkronisasi)."""
        if self.queue.empty():
            return
        event = await self.queue.get()
        key = (event.topic, event.event_id)
        if not self.dedup_store.is_duplicate(*key):
            self.dedup_store.add(*key)
            self.stats.increment_received()
            print(f"Processed event: {event.event_id}")
        else:
            self.stats.increment_duplicate()
            print(f"Duplicate dropped: {event.event_id}")
        self.queue.task_done()

    async def worker(self):
        """Worker background (loop terus)."""
        while True:
            await self.worker_once()
            await asyncio.sleep(0.1)
