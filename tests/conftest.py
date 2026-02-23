import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.fixture
def mock_redis():
    """
    Returns a mock Redis client where all async methods are AsyncMocks.
    Used to patch `app.core.redis_client.redis_client` in tests.
    """
    mock = AsyncMock()
    # hset, hget, hgetall, rpush, lrange, lpop, set, delete all become coroutines
    return mock


@pytest_asyncio.fixture
async def async_client():
    """
    An httpx AsyncClient wired to the FastAPI app via ASGITransport.
    Use this for integration/API tests.
    """
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client
