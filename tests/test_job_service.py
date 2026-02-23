import json
import pytest
from unittest.mock import AsyncMock, patch
from app.services.job_service import JobService
from app.models.job import JobCreate


@pytest.mark.asyncio
async def test_create_job_stores_in_redis_and_returns_response():
    """
    create_job() should:
    1. Store job data in Redis as a hash
    2. Enqueue the job ID
    3. Return the correct JobResponse dict
    """
    with patch("app.services.job_service.redis_client") as mock_redis, \
         patch("app.services.job_service.QueueService.enqueue", new_callable=AsyncMock) as mock_enqueue:

        mock_redis.hset = AsyncMock()

        payload = JobCreate(input_data={"task": "hello"})
        service = JobService()
        result = await service.create_job(payload)

        # hset should be called once with the job hash
        mock_redis.hset.assert_called_once()
        call_kwargs = mock_redis.hset.call_args

        # The key should follow the pattern job:{uuid}
        key_arg = call_kwargs[0][0]
        assert key_arg.startswith("job:")

        # The job should be enqueued
        mock_enqueue.assert_called_once()

        # The response dict should match the expected shape
        assert result["status"] == "queued"
        assert result["input_data"] == {"task": "hello"}
        assert result["result"] is None
        assert "id" in result


@pytest.mark.asyncio
async def test_get_job_returns_deserialized_data():
    """get_job() should fetch the Redis hash and deserialize JSON fields."""
    with patch("app.services.job_service.redis_client") as mock_redis:
        mock_redis.hgetall = AsyncMock(return_value={
            "id": "test-id",
            "status": "completed",
            "input_data": json.dumps({"task": "hello"}),
            "result": json.dumps({"success": True}),
        })

        service = JobService()
        result = await service.get_job("test-id")

        assert result["status"] == "completed"
        assert result["input_data"] == {"task": "hello"}
        assert result["result"] == {"success": True}


@pytest.mark.asyncio
async def test_get_job_raises_when_not_found():
    """get_job() should raise ValueError when the job hash doesn't exist in Redis."""
    with patch("app.services.job_service.redis_client") as mock_redis:
        mock_redis.hgetall = AsyncMock(return_value={})

        service = JobService()
        with pytest.raises(ValueError, match="Job not found"):
            await service.get_job("nonexistent-id")
