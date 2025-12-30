from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, distinct, cast, Date, desc
from datetime import datetime, timedelta
from typing import List

from app.database import get_async_db
from app.models import User, URL, Click
from app.schemas import (
    ClickResponse,
    AnalyticsSummary,
    EnhancedAnalytics,
    TopURLResponse,
    DailyClickStats
)
from app.dependencies import get_current_active_user
from app.cache import cache
from app.config import settings

# ✅ FIXED PREFIX
router = APIRouter(
    prefix="/api/v1/analytics",
    tags=["Analytics"]
)


@router.get("/{short_code}/clicks", response_model=list[ClickResponse])
async def get_url_clicks(
    short_code: str,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user)
):
    url = await db.scalar(
        select(URL).where(and_(
            URL.short_code == short_code,
            URL.owner_id == current_user.id
        ))
    )

    if not url:
        raise HTTPException(status_code=404, detail="URL not found")

    result = await db.execute(
        select(Click)
        .where(Click.url_id == url.id)
        .order_by(Click.clicked_at.desc())
        .offset(skip)
        .limit(limit)
    )

    return result.scalars().all()


@router.get("/{short_code}/summary", response_model=AnalyticsSummary)
async def get_url_analytics_summary(
    short_code: str,
    days: int = Query(default=30, ge=1, le=365),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user)
):
    url = await db.scalar(
        select(URL).where(and_(
            URL.short_code == short_code,
            URL.owner_id == current_user.id
        ))
    )

    if not url:
        raise HTTPException(status_code=404, detail="URL not found")

    start_date = datetime.utcnow() - timedelta(days=days)

    total_clicks = await db.scalar(
        select(func.count(Click.id)).where(
            and_(Click.url_id == url.id, Click.clicked_at >= start_date)
        )
    ) or 0

    total_clicks += await cache.get_click_count(short_code)

    unique_ips = await db.scalar(
        select(func.count(distinct(Click.ip_address))).where(
            and_(Click.url_id == url.id, Click.clicked_at >= start_date)
        )
    ) or 0

    return AnalyticsSummary(
        total_clicks=total_clicks,
        unique_ips=unique_ips,
        top_referrers=[],
        clicks_by_date=[],
        clicks_by_country=[]
    )


@router.get("/{short_code}/enhanced", response_model=EnhancedAnalytics)
async def get_enhanced_analytics(
    short_code: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user)
):
    url = await db.scalar(
        select(URL).where(and_(
            URL.short_code == short_code,
            URL.owner_id == current_user.id
        ))
    )

    if not url:
        raise HTTPException(status_code=404, detail="URL not found")

    total_clicks = await db.scalar(
        select(func.count(Click.id)).where(Click.url_id == url.id)
    ) or 0

    cached = await cache.get_click_count(short_code)
    total_clicks += cached

    unique_visitors = await db.scalar(
        select(func.count(distinct(Click.ip_address))).where(Click.url_id == url.id)
    ) or 0

    return EnhancedAnalytics(
        short_code=short_code,
        total_clicks=total_clicks,
        unique_visitors=unique_visitors,
        clicks_today=cached,
        clicks_this_week=total_clicks,
        clicks_this_month=total_clicks,
        clicks_daily=[],
        top_referrers=[],
        avg_clicks_per_day=round(
            total_clicks / max((datetime.now(url.created_at.tzinfo) - url.created_at).days, 1), 2

        )
    )


@router.get("/top", response_model=List[TopURLResponse])
async def get_top_urls(
    limit: int = Query(default=10, ge=1, le=50),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user)
):
    result = await db.execute(
        select(URL, func.count(Click.id))
        .outerjoin(Click, Click.url_id == URL.id)
        .where(URL.owner_id == current_user.id)
        .group_by(URL.id)
        .order_by(desc(func.count(Click.id)))
        .limit(limit)
    )

    return [
        TopURLResponse(
            id=url.id,
            short_code=url.short_code,
            short_url=f"{settings.BASE_URL}/{url.short_code}",
            title=url.title,
            original_url=url.original_url,
            total_clicks=(count or 0) + await cache.get_click_count(url.short_code),
            created_at=url.created_at
        )
        for url, count in result
    ]
