import json
from datetime import datetime, timezone
from app.core.logging import logger
from app.core.redis_client import redis_client

async def emit_event(event_type: str, payload: dict) -> None:
    """
    Emit a system event:
    - Logs it to the console (structured)
    - Persists it to a Redis list so it can be retrieved via the API

    Redis key: event_log:{job_id}   (a list of JSON strings, ordered by time)
    """
    event = {
        "event": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "payload": payload,
    }

    logger.info(event)

    # Persist to Redis if the event carries a job_id
    job_id = payload.get("job_id")
    if job_id:
        await redis_client.rpush(f"event_log:{job_id}", json.dumps(event))