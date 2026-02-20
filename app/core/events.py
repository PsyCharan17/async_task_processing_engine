from datetime import datetime
from app.core.logging import logger

async def emit_event(event_type: str, payload: dict):
    logger.info({
        "event": event_type,
        "timestamp": datetime.utcnow().isoformat(),
        "payload": payload
    })