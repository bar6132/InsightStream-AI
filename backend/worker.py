"""
InsightStream AI — Background Worker
- Runs the ingestion pipeline immediately on startup
- Repeats automatically every 6 hours
- Also listens to RabbitMQ for manual triggers (e.g. "Fetch News" button)
"""
import asyncio
import json
import os
import sys

import aio_pika
from apscheduler.schedulers.asyncio import AsyncIOScheduler

sys.path.insert(0, os.path.dirname(__file__))

from app.services.ingestion import ingestion_service
from app.services.ollama_fallback import ollama_fallback

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
QUEUE_NAME = "ingestion_tasks"
SCHEDULE_HOURS = 6


async def run_pipeline() -> None:
    print("🔄 Running ingestion pipeline...")
    try:
        results = await ingestion_service.run_pipeline()
        print(f"✅ Pipeline finished: {results}")
    except Exception as e:
        print(f"❌ Pipeline error: {e}")


async def handle_message(message: aio_pika.abc.AbstractIncomingMessage) -> None:
    async with message.process():
        body = json.loads(message.body.decode())
        print(f"📨 Manual trigger received: {body}")
        await run_pipeline()


async def main() -> None:
    print("🐰 InsightStream Worker starting...")

    # Initialize Ollama fallback
    print("🔄 Initializing Ollama fallback model...")
    is_ollama_healthy = await ollama_fallback.check_health()
    if not is_ollama_healthy:
        print("⚠️ Ollama not healthy, pulling model...")
        await ollama_fallback.pull_model()
    else:
        print("✅ Ollama is ready")

    # --- Scheduler: run now + every 6 hours ---
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        run_pipeline,
        trigger="interval",
        hours=SCHEDULE_HOURS,
        id="auto_ingestion",
        max_instances=1,
    )
    scheduler.start()
    print(f"⏰ Scheduler active — pipeline runs every {SCHEDULE_HOURS}h")

    # Run immediately on startup
    await run_pipeline()

    # --- RabbitMQ: listen for manual triggers ---
    print(f"   Connecting to RabbitMQ at: {RABBITMQ_URL}")
    connection = await aio_pika.connect_robust(
        RABBITMQ_URL,
        reconnect_interval=5,
    )

    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=1)
        queue = await channel.declare_queue(QUEUE_NAME, durable=True)
        await queue.consume(handle_message)
        print(f"✅ Worker listening on queue '{QUEUE_NAME}' — waiting for jobs...")
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
