import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_register_user():
    """Test user registration"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "testpassword123"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert "id" in data


@pytest.mark.asyncio
async def test_register_duplicate_username():
    """Test registering with duplicate username"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # First registration
        await client.post(
            "/api/auth/register",
            json={
                "username": "duplicate",
                "email": "first@example.com",
                "password": "password123"
            }
        )
        
        # Duplicate registration
        response = await client.post(
            "/api/auth/register",
            json={
                "username": "duplicate",
                "email": "second@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == 400


@pytest.mark.asyncio
async def test_login():
    """Test user login"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Register user
        await client.post(
            "/api/auth/register",
            json={
                "username": "logintest",
                "email": "login@example.com",
                "password": "password123"
            }
        )
        
        # Login
        response = await client.post(
            "/api/auth/login",
            data={
                "username": "logintest",
                "password": "password123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password():
    """Test login with wrong password"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Register user
        await client.post(
            "/api/auth/register",
            json={
                "username": "wrongpass",
                "email": "wrongpass@example.com",
                "password": "correctpassword"
            }
        )
        
        # Login with wrong password
        response = await client.post(
            "/api/auth/login",
            data={
                "username": "wrongpass",
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401