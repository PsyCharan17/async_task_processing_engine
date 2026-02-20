from app.core.redis_client import redis_client


class QueueService:
    @staticmethod
    async def enqueue(queue_name: str, job_id: str) -> None:
        await redis_client.rpush(queue_name, job_id)

    @staticmethod
    async def dequeue(queue_name: str) -> str | None:
        return await redis_client.lpop(queue_name)
