import pytest
from httpx import AsyncClient
from app.main import app


async def get_auth_token_and_create_url():
    """Helper function to get token and create URL"""
    async with AsyncClient(app=app, base_url="http://test", follow_redirects=False) as client:
        # Register user
        await client.post(
            "/api/auth/register",
            json={
                "username": "analyticsuser",
                "email": "analytics@example.com",
                "password": "password123"
            }
        )
        
        # Login
        login_response = await client.post(
            "/api/auth/login",
            data={
                "username": "analyticsuser",
                "password": "password123"
            }
        )
        token = login_response.json()["access_token"]
        
        # Create URL
        url_response = await client.post(
            "/api/urls",
            json={
                "original_url": "https://www.example.com",
                "title": "Analytics Test"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        short_code = url_response.json()["short_code"]
        
        # Generate some clicks
        for _ in range(5):
            await client.get(f"/{short_code}")
        
        return token, short_code


@pytest.mark.asyncio
async def test_get_url_clicks():
    """Test getting clicks for a URL"""
    token, short_code = await get_auth_token_and_create_url()
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            f"/api/analytics/{short_code}/clicks",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 5


@pytest.mark.asyncio
async def test_get_analytics_summary():
    """Test getting analytics summary"""
    token, short_code = await get_auth_token_and_create_url()
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            f"/api/analytics/{short_code}/summary",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_clicks" in data
        assert "unique_ips" in data
        assert "top_referrers" in data
        assert "clicks_by_date" in data
        assert data["total_clicks"] == 5


@pytest.mark.asyncio
async def test_analytics_unauthorized():
    """Test accessing analytics without authorization"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/analytics/test123/summary")
        assert response.status_code == 401