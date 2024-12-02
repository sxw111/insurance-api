import asyncio
import json
from datetime import datetime
from typing import Optional

from .config import settings

kafka_producer = None
log_buffer = []
log_lock = asyncio.Lock()


async def batch_sender():
    global kafka_producer, log_buffer
    while True:
        await asyncio.sleep(settings.BATCH_TIMEOUT)
        async with log_lock:
            if not kafka_producer:
                continue
            if log_buffer:
                await send_logs_to_kafka(log_buffer)
                log_buffer = []


async def send_logs_to_kafka(messages):
    global kafka_producer
    if not kafka_producer:
        raise RuntimeError("Kafka producer is not initialized")
    for message in messages:
        await kafka_producer.send_and_wait(
            settings.KAFKA_TOPIC, json.dumps(message).encode("utf-8")
        )


async def log_action(action: str, tariff_id: Optional[int] = None):
    global log_buffer
    log_entry = {
        "action": action,
        "tariff_id": tariff_id,
        "timestamp": datetime.utcnow().isoformat(),
    }
    async with log_lock:
        log_buffer.append(log_entry)
        if len(log_buffer) >= settings.BATCH_SIZE:
            await send_logs_to_kafka(log_buffer)
            log_buffer = []
