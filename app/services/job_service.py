import uuid
import json
from app.core.redis_client import redis_client
from app.services.queue_service import QueueService

class JobService:
    QUEUE = "job_queue"

    async def create_job(self, data):
        job_id = str(uuid.uuid4())
        job = {
            "id": job_id,
            "status": "queued",
            "input_data": json.dumps(data.input_data),
            "result": json.dumps(None),
        }
        await redis_client.hset(f"job:{job_id}", mapping=job)
        await QueueService.enqueue(self.QUEUE, job_id)
        # Return a dict with deserialized fields for the response
        return {
            "id": job_id,
            "status": "queued",
            "input_data": data.input_data,
            "result": None,
        }

    async def get_job(self, job_id: str):
        job = await redis_client.hgetall(f"job:{job_id}")
        if not job:
            raise ValueError("Job not found")
        # Deserialize JSON fields back to Python objects
        job["input_data"] = json.loads(job["input_data"])
        job["result"] = json.loads(job["result"]) if job.get("result") else None
        return job