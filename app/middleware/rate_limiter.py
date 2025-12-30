from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime, timedelta
import redis.asyncio as redis
from app.config import settings


class RateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, redis_url: str = None):
        super().__init__(app)
        self.redis_url = redis_url or settings.REDIS_URL
        self.redis_client = None
        self.rate_limit = settings.RATE_LIMIT_PER_MINUTE
    
    async def dispatch(self, request: Request, call_next):
        # Initialize Redis client if not already done
        if self.redis_client is None:
            self.redis_client = await redis.from_url(self.redis_url, decode_responses=True)
        
        # Get client IP
        client_ip = request.client.host
        
        # Create rate limit key
        now = datetime.utcnow()
        minute_key = f"rate_limit:{client_ip}:{now.strftime('%Y%m%d%H%M')}"
        
        try:
            # Increment counter
            current_count = await self.redis_client.incr(minute_key)
            
            # Set expiry on first request
            if current_count == 1:
                await self.redis_client.expire(minute_key, 60)
            
            # Check if rate limit exceeded
            if current_count > self.rate_limit:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded. Please try again later."
                )
            
            # Process request
            response = await call_next(request)
            
            # Add rate limit headers
            response.headers["X-RateLimit-Limit"] = str(self.rate_limit)
            response.headers["X-RateLimit-Remaining"] = str(max(0, self.rate_limit - current_count))
            response.headers["X-RateLimit-Reset"] = str(int((now + timedelta(minutes=1)).timestamp()))
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            # If Redis is down, allow the request
            print(f"Rate limiter error: {e}")
            return await call_next(request)