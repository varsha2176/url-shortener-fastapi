import redis.asyncio as redis
from typing import Optional
import json
from app.config import settings


class RedisCache:
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
    
    async def connect(self):
        """Initialize Redis connection"""
        if not self.redis_client:
            self.redis_client = await redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                encoding="utf-8"
            )
    
    async def disconnect(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
    
    async def get_url(self, short_code: str) -> Optional[str]:
        """Get original URL from cache"""
        if not self.redis_client:
            await self.connect()
        
        try:
            cached_url = await self.redis_client.get(f"url:{short_code}")
            return cached_url
        except Exception as e:
            print(f"Redis GET error: {e}")
            return None
    
    async def set_url(self, short_code: str, original_url: str, expire: int = 3600):
        """Cache URL mapping"""
        if not self.redis_client:
            await self.connect()
        
        try:
            await self.redis_client.setex(
                f"url:{short_code}",
                expire,
                original_url
            )
        except Exception as e:
            print(f"Redis SET error: {e}")
    
    async def delete_url(self, short_code: str):
        """Remove URL from cache"""
        if not self.redis_client:
            await self.connect()
        
        try:
            await self.redis_client.delete(f"url:{short_code}")
        except Exception as e:
            print(f"Redis DELETE error: {e}")
    
    # ✅ Renamed method to match router call
    async def increment_clicks(self, short_code: str) -> int:
        """Increment click count in cache"""
        if not self.redis_client:
            await self.connect()
        
        try:
            key = f"clicks:{short_code}"
            count = await self.redis_client.incr(key)
            # Set expiry on first increment
            if count == 1:
                await self.redis_client.expire(key, 300)  # 5 minutes
            return count
        except Exception as e:
            print(f"Redis INCR error: {e}")
            return 0
    
    async def get_click_count(self, short_code: str) -> int:
        """Get cached click count"""
        if not self.redis_client:
            await self.connect()
        
        try:
            count = await self.redis_client.get(f"clicks:{short_code}")
            return int(count) if count else 0
        except Exception as e:
            print(f"Redis GET clicks error: {e}")
            return 0
    
    async def reset_click_count(self, short_code: str):
        """Reset click count cache"""
        if not self.redis_client:
            await self.connect()
        
        try:
            await self.redis_client.delete(f"clicks:{short_code}")
        except Exception as e:
            print(f"Redis DELETE clicks error: {e}")


# Global cache instance
cache = RedisCache()
