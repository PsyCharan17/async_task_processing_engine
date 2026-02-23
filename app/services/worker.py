import asyncio
import json
from app.services.queue_service import QueueService
from app.core.redis_client import redis_client
from app.core.events import emit_event

MAX_RETRIES = 3

async def process_job(job_id: str) -> None:
    """
    Process a single job with:
    - Idempotency: skip if already completed, use a Redis lock to prevent double-processing
    - Retry + exponential backoff: up to MAX_RETRIES attempts on failure
    """
    job_key = f"job:{job_id}"
    lock_key = f"lock:job:{job_id}"

    # --- Idempotency Guard 1: Skip if already completed ---
    current_status = await redis_client.hget(job_key, "status")
    if current_status == "completed":
        return

    # --- Idempotency Guard 2: Acquire a Redis SETNX lock (60s TTL) ---
    # SETNX (Set if Not eXists) ensures only one worker processes this job at a time
    acquired = await redis_client.set(lock_key, "1", nx=True, ex=60)
    if not acquired:
        # Another worker already holds the lock for this job
        return

    try:
        for attempt in range(MAX_RETRIES):
            try:
                await redis_client.hset(job_key, mapping={
                    "status": "processing",
                    "retry_count": str(attempt),
                })
                await emit_event("job_started", {"job_id": job_id, "attempt": attempt + 1})

                # --- Simulated work ---
                # Replace this with real work (e.g. an LLM call, file processing, etc.)
                await asyncio.sleep(2)

                # --- Success ---
                await redis_client.hset(job_key, mapping={
                    "status": "completed",
                    "result": json.dumps({"success": True}),
                })
                await emit_event("job_completed", {"job_id": job_id})
                return  # done, exit the retry loop

            except Exception as exc:
                if attempt < MAX_RETRIES - 1:
                    # Exponential backoff: wait 1s, 2s, 4s between retries
                    backoff = 2 ** attempt
                    await emit_event("job_retrying", {
                        "job_id": job_id,
                        "attempt": attempt + 1,
                        "error": str(exc),
                        "backoff_seconds": backoff,
                    })
                    await asyncio.sleep(backoff)
                else:
                    # All retries exhausted — mark as failed
                    await redis_client.hset(job_key, mapping={
                        "status": "failed",
                        "retry_count": str(attempt + 1),
                    })
                    await emit_event("job_failed", {
                        "job_id": job_id,
                        "error": str(exc),
                        "total_attempts": attempt + 1,
                    })
    finally:
        # Always release the lock when done (success or failure)
        await redis_client.delete(lock_key)


async def worker_loop(queue_name: str) -> None:
    """
    Continuously polls the Redis queue for new job IDs and processes them.
    """
    while True:
        job_id = await QueueService.dequeue(queue_name)
        if job_id:
            await process_job(job_id)
        else:
            await asyncio.sleep(0.1)
