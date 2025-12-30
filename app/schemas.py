from pydantic import BaseModel, EmailStr, HttpUrl, Field
from typing import Optional, List, Dict
from datetime import datetime


# -----------------------
# User Schemas
# -----------------------
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str
    password: str

# -----------------------
# Token Schemas
# -----------------------
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# -----------------------
# URL Schemas
# -----------------------
class URLCreate(BaseModel):
    original_url: HttpUrl
    custom_short_code: Optional[str] = Field(None, min_length=4, max_length=10)  # ✅ FIXED
    title: Optional[str] = Field(None, max_length=255)
    expires_at: Optional[datetime] = None

class URLResponse(BaseModel):
    id: int
    original_url: str
    short_code: str
    short_url: str
    title: Optional[str]
    is_active: bool
    owner_id: int
    created_at: datetime
    expires_at: Optional[datetime]
    click_count: int = 0
    
    class Config:
        from_attributes = True

class URLUpdate(BaseModel):
    title: Optional[str] = None
    is_active: Optional[bool] = None

# -----------------------
# Analytics Schemas
# -----------------------
class ClickCreate(BaseModel):
    url_id: int
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    referrer: Optional[str] = None
    country: Optional[str] = None

class ClickResponse(BaseModel):
    id: int
    url_id: int
    ip_address: Optional[str]
    user_agent: Optional[str]
    referrer: Optional[str]
    country: Optional[str]
    clicked_at: datetime
    
    class Config:
        from_attributes = True

class AnalyticsSummary(BaseModel):
    total_clicks: int
    unique_ips: int
    top_referrers: List[Dict]
    clicks_by_date: List[Dict]
    clicks_by_country: List[Dict]

# -----------------------
# Enhanced Analytics Schemas
# -----------------------
class DailyClickStats(BaseModel):
    date: str
    count: int


class TopURLResponse(BaseModel):
    id: int
    short_code: str
    short_url: str
    title: Optional[str]
    original_url: str
    total_clicks: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class EnhancedAnalytics(BaseModel):
    short_code: str
    total_clicks: int
    unique_visitors: int
    clicks_today: int
    clicks_this_week: int
    clicks_this_month: int
    clicks_daily: list[DailyClickStats]
    top_referrers: list[dict]
    avg_clicks_per_day: float


class DashboardStats(BaseModel):
    total_urls: int
    active_urls: int
    total_clicks: int
    clicks_today: int
    clicks_this_week: int
    clicks_this_month: int
    avg_clicks_per_url: float
    daily_clicks: list[DailyClickStats]