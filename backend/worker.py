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
SCHEDULE_HOURS = 3


async def run_pipeline() -> None:
    print("=" * 50)
    print("🔄 [PIPELINE] Starting ingestion run...")
    print("=" * 50)
    try:
        results = await ingestion_service.run_pipeline()
        print("=" * 50)
        print(f"✅ [PIPELINE] Done — added: {results['added']} | skipped: {results['skipped']} | errors: {results['errors']}")
        print("=" * 50)
    except Exception as e:
        print(f"❌ [PIPELINE] Fatal error: {e}")


async def handle_message(message: aio_pika.abc.AbstractIncomingMessage) -> None:
    async with message.process():
        body = json.loads(message.body.decode())
        print(f"📨 Manual trigger received: {body}")
        await run_pipeline()


async def main() -> None:
    print("=" * 50)
    print("🚀 [1/4] InsightStream Worker starting...")
    print("=" * 50)

    # [STEP 1] Ollama
    print("🔄 [2/4] Checking Ollama fallback...")
    is_ollama_healthy = await ollama_fallback.check_health()
    if not is_ollama_healthy:
        print("⚠️  Ollama has no model loaded — pulling llama2 (this may take a few minutes)...")
        success = await ollama_fallback.pull_model()
        if success:
            print("✅ Ollama model ready")
        else:
            print("⚠️  Ollama pull failed — will use Groq only")
    else:
        print("✅ Ollama is ready")

    # [STEP 2] Scheduler
    print(f"⏰ [3/4] Starting scheduler — pipeline every {SCHEDULE_HOURS} hours...")
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        run_pipeline,
        trigger="interval",
        hours=SCHEDULE_HOURS,
        id="auto_ingestion",
        max_instances=1,
    )
    scheduler.start()
    print(f"✅ Scheduler active — next run in {SCHEDULE_HOURS}h")

    # [STEP 3] Run immediately on startup
    print("🔄 [4/4] Running first pipeline now...")
    await run_pipeline()

    # [STEP 4] RabbitMQ listener
    print(f"📡 Connecting to RabbitMQ at: {RABBITMQ_URL}")
    connection = await aio_pika.connect_robust(
        RABBITMQ_URL,
        reconnect_interval=5,
    )

    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=1)
        queue = await channel.declare_queue(QUEUE_NAME, durable=True)
        await queue.consume(handle_message)
        print(f"✅ Worker ready — listening on queue '{QUEUE_NAME}'")
        print("=" * 50)
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
