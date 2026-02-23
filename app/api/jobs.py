import json
from fastapi import APIRouter, HTTPException
from app.services.job_service import JobService
from app.models.job import JobCreate, JobResponse
from app.core.redis_client import redis_client

router = APIRouter()
service = JobService()


@router.post("/", response_model=JobResponse)
async def create_job(payload: JobCreate):
    return await service.create_job(payload)


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: str):
    try:
        return await service.get_job(job_id)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found")


@router.get("/{job_id}/events")
async def get_job_events(job_id: str):
    """
    Returns the ordered list of events emitted for a job.
    Events are stored in Redis as: event_log:{job_id}
    """
    raw_events = await redis_client.lrange(f"event_log:{job_id}", 0, -1)
    if not raw_events:
        raise HTTPException(status_code=404, detail=f"No events found for job '{job_id}'")
    return {"job_id": job_id, "events": [json.loads(e) for e in raw_events]}
