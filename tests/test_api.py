import json
import pytest
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_create_job_returns_201_shape(async_client):
    """
    POST /jobs/ with valid input should return 200
    with the expected job response shape (id, status=queued, input_data, result=None).
    """
    with patch("app.services.job_service.redis_client") as mock_redis, \
         patch("app.services.job_service.QueueService.enqueue", new_callable=AsyncMock), \
         patch("app.services.worker.redis_client"), \
         patch("app.services.worker.QueueService.dequeue", new_callable=AsyncMock, return_value=None):

        mock_redis.hset = AsyncMock()

        response = await async_client.post("/jobs/", json={"input_data": {"task": "hello"}})

        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "queued"
        assert body["input_data"] == {"task": "hello"}
        assert body["result"] is None
        assert "id" in body


@pytest.mark.asyncio
async def test_get_job_returns_job_data(async_client):
    """GET /jobs/{id} should return the job data when the job exists."""
    job_id = "test-uuid-1234"

    with patch("app.services.job_service.redis_client") as mock_redis:
        mock_redis.hgetall = AsyncMock(return_value={
            "id": job_id,
            "status": "completed",
            "input_data": json.dumps({"task": "hello"}),
            "result": json.dumps({"success": True}),
        })

        response = await async_client.get(f"/jobs/{job_id}")

        assert response.status_code == 200
        body = response.json()
        assert body["id"] == job_id
        assert body["status"] == "completed"
        assert body["result"] == {"success": True}


@pytest.mark.asyncio
async def test_get_job_returns_404_when_not_found(async_client):
    """GET /jobs/{id} should return 404 when the job doesn't exist in Redis."""
    with patch("app.services.job_service.redis_client") as mock_redis:
        mock_redis.hgetall = AsyncMock(return_value={})

        response = await async_client.get("/jobs/nonexistent-id")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_job_events_returns_event_list(async_client):
    """GET /jobs/{id}/events should return the ordered list of events for a job."""
    job_id = "test-uuid-1234"
    events = [
        json.dumps({"event": "job_started", "timestamp": "2024-01-01T00:00:00+00:00", "payload": {"job_id": job_id}}),
        json.dumps({"event": "job_completed", "timestamp": "2024-01-01T00:00:05+00:00", "payload": {"job_id": job_id}}),
    ]

    with patch("app.api.jobs.redis_client") as mock_redis:
        mock_redis.lrange = AsyncMock(return_value=events)

        response = await async_client.get(f"/jobs/{job_id}/events")

        assert response.status_code == 200
        body = response.json()
        assert body["job_id"] == job_id
        assert len(body["events"]) == 2
        assert body["events"][0]["event"] == "job_started"
        assert body["events"][1]["event"] == "job_completed"


@pytest.mark.asyncio
async def test_get_job_events_returns_404_when_no_events(async_client):
    """GET /jobs/{id}/events should return 404 when there are no events."""
    with patch("app.api.jobs.redis_client") as mock_redis:
        mock_redis.lrange = AsyncMock(return_value=[])

        response = await async_client.get("/jobs/no-events-job/events")

        assert response.status_code == 404
