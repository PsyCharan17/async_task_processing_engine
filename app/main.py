import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.jobs import router as jobs_router
from app.services.worker import worker_loop

QUEUE_NAME = "job_queue"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start the worker in the background when the server starts
    task = asyncio.create_task(worker_loop(QUEUE_NAME))
    yield
    # Shut down the worker when the server stops
    task.cancel()

app = FastAPI(title="Async Task Engine", lifespan=lifespan)

app.include_router(jobs_router, prefix="/jobs", tags=["jobs"])


