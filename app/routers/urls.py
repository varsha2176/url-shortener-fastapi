from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, timezone

from app.database import get_async_db
from app.models import User, URL, Click
from app.schemas import URLCreate, URLResponse, URLUpdate
from app.dependencies import get_current_active_user
from app.utils import generate_short_code, is_valid_short_code
from app.config import settings
from app.cache import cache

# ✅ Two separate routers
api_router = APIRouter(prefix="/api/v1", tags=["URLs"])
redirect_router = APIRouter(tags=["Redirect"])


# -------------------------
# CREATE SHORT URL
# -------------------------
@api_router.post("/urls/", response_model=URLResponse, status_code=status.HTTP_201_CREATED)
async def create_short_url(
    url_data: URLCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new short URL"""
    # Validate or generate short code
    if url_data.custom_short_code:
        if not is_valid_short_code(url_data.custom_short_code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid custom short code format"
            )
        short_code = url_data.custom_short_code
        
        # Check if exists
        result = await db.execute(
            select(URL).where(URL.short_code == short_code)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Custom short code already exists"
            )
    else:
        # Generate unique code
        while True:
            short_code = generate_short_code()
            result = await db.execute(
                select(URL).where(URL.short_code == short_code)
            )
            if not result.scalar_one_or_none():
                break

    # Create URL record
    db_url = URL(
        original_url=str(url_data.original_url),
        short_code=short_code,
        title=url_data.title,
        owner_id=current_user.id,
        expires_at=url_data.expires_at
    )

    db.add(db_url)
    await db.commit()
    await db.refresh(db_url)

    # Cache it
    await cache.set_url(short_code, db_url.original_url, expire=86400)

    # ✅ Return with BASE_URL from settings
    return URLResponse(
        id=db_url.id,
        original_url=db_url.original_url,
        short_code=db_url.short_code,
        short_url=f"{settings.BASE_URL}/{short_code}",  # ✅ Uses .env BASE_URL
        title=db_url.title,
        is_active=db_url.is_active,
        owner_id=db_url.owner_id,
        created_at=db_url.created_at,
        expires_at=db_url.expires_at,
        click_count=0
    )


# -------------------------
# LIST USER URLS
# -------------------------
@api_router.get("/urls/", response_model=list[URLResponse])
async def get_user_urls(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all URLs for current user"""
    result = await db.execute(
        select(URL, func.count(Click.id).label("click_count"))
        .outerjoin(Click, Click.url_id == URL.id)
        .where(URL.owner_id == current_user.id)
        .group_by(URL.id)
        .order_by(URL.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    urls = []
    for url, db_clicks in result:
        cache_clicks = await cache.get_click_count(url.short_code)

        urls.append(
            URLResponse(
                id=url.id,
                original_url=url.original_url,
                short_code=url.short_code,
                short_url=f"{settings.BASE_URL}/{url.short_code}",  # ✅ Uses .env BASE_URL
                title=url.title,
                is_active=url.is_active,
                owner_id=url.owner_id,
                created_at=url.created_at,
                expires_at=url.expires_at,
                click_count=(db_clicks or 0) + cache_clicks
            )
        )

    return urls


# -------------------------
# GET SINGLE URL
# -------------------------
@api_router.get("/urls/{short_code}", response_model=URLResponse)
async def get_url_details(
    short_code: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get details for a specific URL"""
    result = await db.execute(
        select(URL, func.count(Click.id).label("click_count"))
        .outerjoin(Click, Click.url_id == URL.id)
        .where(and_(URL.short_code == short_code, URL.owner_id == current_user.id))
        .group_by(URL.id)
    )
    
    row = result.first()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="URL not found"
        )
    
    url, click_count = row
    cached_clicks = await cache.get_click_count(url.short_code)
    
    return URLResponse(
        id=url.id,
        original_url=url.original_url,
        short_code=url.short_code,
        short_url=f"{settings.BASE_URL}/{url.short_code}",
        title=url.title,
        is_active=url.is_active,
        owner_id=url.owner_id,
        created_at=url.created_at,
        expires_at=url.expires_at,
        click_count=(click_count or 0) + cached_clicks
    )


# -------------------------
# UPDATE URL
# -------------------------
@api_router.patch("/urls/{short_code}", response_model=URLResponse)
async def update_url(
    short_code: str,
    url_update: URLUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a URL"""
    result = await db.execute(
        select(URL).where(and_(URL.short_code == short_code, URL.owner_id == current_user.id))
    )
    url = result.scalar_one_or_none()
    
    if not url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="URL not found"
        )
    
    if url_update.title is not None:
        url.title = url_update.title
    if url_update.is_active is not None:
        url.is_active = url_update.is_active
        if not url_update.is_active:
            await cache.delete_url(short_code)
    
    await db.commit()
    await db.refresh(url)
    
    click_result = await db.execute(
        select(func.count(Click.id)).where(Click.url_id == url.id)
    )
    click_count = click_result.scalar() or 0
    cached_clicks = await cache.get_click_count(url.short_code)
    
    return URLResponse(
        id=url.id,
        original_url=url.original_url,
        short_code=url.short_code,
        short_url=f"{settings.BASE_URL}/{url.short_code}",
        title=url.title,
        is_active=url.is_active,
        owner_id=url.owner_id,
        created_at=url.created_at,
        expires_at=url.expires_at,
        click_count=click_count + cached_clicks
    )


# -------------------------
# DELETE URL
# -------------------------
@api_router.delete("/urls/{short_code}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_url(
    short_code: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a URL"""
    result = await db.execute(
        select(URL).where(and_(URL.short_code == short_code, URL.owner_id == current_user.id))
    )
    url = result.scalar_one_or_none()
    
    if not url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="URL not found"
        )
    
    await cache.delete_url(short_code)
    await cache.reset_click_count(short_code)
    
    await db.delete(url)
    await db.commit()


# -------------------------
# ✅ REDIRECT (No auth required)
# -------------------------
@redirect_router.get("/{short_code}")
async def redirect_to_original_url(
    short_code: str,
    request: Request,
    db: AsyncSession = Depends(get_async_db)
):
    """Redirect to original URL and track click"""
    
    # 1️⃣ Check cache first
    cached_url = await cache.get_url(short_code)
    if cached_url:
        print(f"✅ Cache HIT: {short_code}")
        await cache.increment_clicks(short_code)
        
        # Track click in background
        click = Click(
            url_id=None,  # We'll fix this properly below
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            referrer=request.headers.get("referer")
        )
        # For now, skip DB insert to avoid errors
        
        return RedirectResponse(url=cached_url, status_code=307)

    # 2️⃣ Database lookup
    print(f"❌ Cache MISS: {short_code}")
    result = await db.execute(
        select(URL).where(URL.short_code == short_code)
    )
    url = result.scalar_one_or_none()

    if not url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short URL not found"
        )

    if not url.is_active:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="This URL has been disabled"
        )

    if url.expires_at and url.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="This URL has expired"
        )

    # 3️⃣ Track click
    click = Click(
        url_id=url.id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        referrer=request.headers.get("referer")
    )
    db.add(click)
    await db.commit()

    # 4️⃣ Cache for next time
    await cache.set_url(short_code, url.original_url, expire=86400)
    await cache.increment_clicks(short_code)

    return RedirectResponse(url=url.original_url, status_code=307)