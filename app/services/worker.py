import asyncio
from app.services.queue_service import QueueService
from app.core.redis_client import redis_client
from app.core.events import emit_event

async def process_job(job_id):
    job_key =f"job:{job_id}"
    await redis_client.hset(job_key, "status", "processing")

    await emit_event("job_started", {"job_id": job_id})
    #simulating work
    await asyncio.sleep(10)

    await redis_client.hset(job_key, mapping={
        "status": "completed",
        "result": '{"success": true}',
    })

    await emit_event("job_completed", {"job_id": job_id})
async def worker_loop(queue_name: str):
    while True:
        job_id = await QueueService.dequeue(queue_name)
        if job_id:
            await process_job(job_id)
        else:
            await asyncio.sleep(0.1)
