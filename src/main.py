import asyncio
import sqlite3
from fastapi import FastAPI

from src.models import Event
from src.dedup_store import DedupStore
from src.consumer import Consumer
from src.stats import Stats

app = FastAPI(title="Pub-Sub Log Aggregator")

dedup_store = DedupStore()
stats = Stats()
consumer = Consumer(dedup_store, stats)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(consumer.worker())

@app.post("/publish")
async def publish(events: list[Event] | Event):
    if isinstance(events, Event):
        events = [events]
    for e in events:
        await consumer.enqueue(e)
    await asyncio.sleep(0.1)
    while not consumer.queue.empty():
        await consumer.worker_once()
    return {"status": "queued", "count": len(events)}

@app.get("/events")
def get_events(topic: str | None = None):
    with sqlite3.connect("dedup_store.db") as conn:
        cursor = conn.cursor()
        if topic:
            cursor.execute("SELECT topic, event_id FROM dedup WHERE topic=?", (topic,))
        else:
            cursor.execute("SELECT topic, event_id FROM dedup")
        rows = cursor.fetchall()
    return {"events": [{"topic": t, "event_id": eid} for t, eid in rows]}

@app.get("/stats")
def get_stats():
    return stats.to_dict()
