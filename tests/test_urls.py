import pytest
from httpx import AsyncClient
from app.main import app


async def get_auth_token():
    """Helper function to get authentication token"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Register user
        await client.post(
            "/api/auth/register",
            json={
                "username": "urluser",
                "email": "urluser@example.com",
                "password": "password123"
            }
        )
        
        # Login
        response = await client.post(
            "/api/auth/login",
            data={
                "username": "urluser",
                "password": "password123"
            }
        )
        return response.json()["access_token"]


@pytest.mark.asyncio
async def test_create_short_url():
    """Test creating a short URL"""
    token = await get_auth_token()
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/urls",
            json={
                "original_url": "https://www.example.com",
                "title": "Example Website"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["original_url"] == "https://www.example.com/"
        assert "short_code" in data
        assert "short_url" in data


@pytest.mark.asyncio
async def test_create_short_url_with_custom_code():
    """Test creating a short URL with custom code"""
    token = await get_auth_token()
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/urls",
            json={
                "original_url": "https://www.google.com",
                "custom_code": "google",
                "title": "Google"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["short_code"] == "google"


@pytest.mark.asyncio
async def test_get_user_urls():
    """Test getting user's URLs"""
    token = await get_auth_token()
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create a URL
        await client.post(
            "/api/urls",
            json={
                "original_url": "https://www.example.com",
                "title": "Example"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Get URLs
        response = await client.get(
            "/api/urls",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0


@pytest.mark.asyncio
async def test_redirect_to_url():
    """Test URL redirection"""
    token = await get_auth_token()
    
    async with AsyncClient(app=app, base_url="http://test", follow_redirects=False) as client:
        # Create a URL
        create_response = await client.post(
            "/api/urls",
            json={
                "original_url": "https://www.example.com",
                "title": "Example"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        short_code = create_response.json()["short_code"]
        
        # Test redirect
        response = await client.get(f"/{short_code}")
        assert response.status_code == 307
        assert response.headers["location"] == "https://www.example.com/"


@pytest.mark.asyncio
async def test_update_url():
    """Test updating a URL"""
    token = await get_auth_token()
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create a URL
        create_response = await client.post(
            "/api/urls",
            json={
                "original_url": "https://www.example.com",
                "title": "Old Title"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        short_code = create_response.json()["short_code"]
        
        # Update URL
        response = await client.patch(
            f"/api/urls/{short_code}",
            json={"title": "New Title"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "New Title"


@pytest.mark.asyncio
async def test_delete_url():
    """Test deleting a URL"""
    token = await get_auth_token()
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create a URL
        create_response = await client.post(
            "/api/urls",
            json={
                "original_url": "https://www.example.com",
                "title": "To Delete"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        short_code = create_response.json()["short_code"]
        
        # Delete URL
        response = await client.delete(
            f"/api/urls/{short_code}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 204