import aio_pika
import json
import os

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
QUEUE_NAME = "ingestion_tasks"


async def publish_ingestion_task(payload: dict = None):
    """
    Publishes a scrape job to the RabbitMQ ingestion queue.
    The worker container picks it up and runs the full pipeline.
    """
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    async with connection:
        channel = await connection.channel()
        await channel.declare_queue(QUEUE_NAME, durable=True)
        message_body = json.dumps(payload or {"task": "scrape_all"}).encode()
        await channel.default_exchange.publish(
            aio_pika.Message(
                body=message_body,
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            ),
            routing_key=QUEUE_NAME,
        )
        print(f"📤 Published job to queue '{QUEUE_NAME}': {payload}")
