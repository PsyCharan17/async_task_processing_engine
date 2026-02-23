import pytest
from unittest.mock import AsyncMock, patch
from app.services.queue_service import QueueService


@pytest.mark.asyncio
async def test_enqueue_calls_rpush():
    """enqueue() should call redis_client.rpush with the right queue name and job ID."""
    with patch("app.services.queue_service.redis_client") as mock_redis:
        mock_redis.rpush = AsyncMock()

        await QueueService.enqueue("job_queue", "abc-123")

        mock_redis.rpush.assert_called_once_with("job_queue", "abc-123")


@pytest.mark.asyncio
async def test_dequeue_returns_job_id():
    """dequeue() should return the job ID popped from the left of the Redis list."""
    with patch("app.services.queue_service.redis_client") as mock_redis:
        mock_redis.lpop = AsyncMock(return_value="abc-123")

        result = await QueueService.dequeue("job_queue")

        assert result == "abc-123"
        mock_redis.lpop.assert_called_once_with("job_queue")


@pytest.mark.asyncio
async def test_dequeue_returns_none_when_empty():
    """dequeue() should return None when the queue is empty."""
    with patch("app.services.queue_service.redis_client") as mock_redis:
        mock_redis.lpop = AsyncMock(return_value=None)

        result = await QueueService.dequeue("job_queue")

        assert result is None
