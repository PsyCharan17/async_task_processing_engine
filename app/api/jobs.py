from fastapi import APIRouter
from app.services.job_service import JobService

#can also use as we have defined it in __init__.py within services directory
# from app.services import JobService

from app.models.job import JobCreate, JobResponse

router = APIRouter()
service = JobService()

@router.post("/",response_model=JobResponse)
async def create_job(payload: JobCreate):
    return await service.create_job(payload)

@router.get("/{job_id}",response_model=JobResponse)
async def get_job(job_id:str):
    return await service.get_job(job_id)

