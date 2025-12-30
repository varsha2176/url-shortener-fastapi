from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.routers import auth, urls, analytics
from app.cache import cache


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    await cache.connect()
    print("✅ Redis cache connected")
    yield
    # Shutdown
    await cache.disconnect()
    print("❌ Redis cache disconnected")


app = FastAPI(
    title="URL Shortener API",
    description="A high-performance URL shortening service with Redis caching",
    version="1.0.0",
    lifespan=lifespan
)

# ✅ CORS Middleware - Allow both localhost and 127.0.0.1
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# ✅ Register routers
app.include_router(auth.router)
app.include_router(urls.api_router)       # API routes at /api/v1/urls/
app.include_router(urls.redirect_router)  # Redirect at /{short_code}
app.include_router(analytics.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to URL Shortener API with Redis Cache",
        "version": "1.0.0",
        "features": [
            "JWT Authentication",
            "URL Shortening",
            "Redis Caching",
            "Analytics",
            "Rate Limiting"
        ],
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        redis_status = await cache.redis_client.ping() if cache.redis_client else False
        return {
            "status": "healthy",
            "redis": "connected" if redis_status else "disconnected"
        }
    except Exception as e:
        return {
            "status": "degraded",
            "redis": "error",
            "error": str(e)
        }