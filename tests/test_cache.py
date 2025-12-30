import pytest
from app.cache import cache


@pytest.mark.asyncio
async def test_redis_connection():
    """Test Redis connection"""
    await cache.connect()
    assert cache.redis_client is not None
    
    # Test ping
    result = await cache.redis_client.ping()
    assert result is True
    
    await cache.disconnect()


@pytest.mark.asyncio
async def test_set_and_get_url():
    """Test caching URL mapping"""
    await cache.connect()
    
    short_code = "test123"
    original_url = "https://www.example.com"
    
    # Set URL
    await cache.set_url(short_code, original_url, expire=60)
    
    # Get URL
    cached_url = await cache.get_url(short_code)
    assert cached_url == original_url
    
    # Delete URL
    await cache.delete_url(short_code)
    cached_url = await cache.get_url(short_code)
    assert cached_url is None
    
    await cache.disconnect()


@pytest.mark.asyncio
async def test_click_count():
    """Test click count caching"""
    await cache.connect()
    
    short_code = "test456"
    
    # Increment clicks
    count1 = await cache.increment_click_count(short_code)
    assert count1 == 1
    
    count2 = await cache.increment_click_count(short_code)
    assert count2 == 2
    
    # Get count
    count = await cache.get_click_count(short_code)
    assert count == 2
    
    # Reset count
    await cache.reset_click_count(short_code)
    count = await cache.get_click_count(short_code)
    assert count == 0
    
    await cache.disconnect()