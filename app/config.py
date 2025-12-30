from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# Load .env file early
load_dotenv()


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "URL Shortener"
    ENVIRONMENT: str = "development"
    BASE_URL: str = "http://localhost:8000"
    SHORT_CODE_LENGTH: int = 6

    # Database
    DATABASE_URL: str
    ASYNC_DATABASE_URL: str

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    class Config:
        env_file = ".env"
        case_sensitive = True


# Create a single settings instance for your app
settings = Settings()

# Optional: quick verification print
if settings.ENVIRONMENT == "development":
    print("Settings loaded successfully:")
    print(f"DATABASE_URL={settings.DATABASE_URL}")
    print(f"ASYNC_DATABASE_URL={settings.ASYNC_DATABASE_URL}")
    print(f"REDIS_URL={settings.REDIS_URL}")
    print(f"SECRET_KEY={settings.SECRET_KEY[:6]}...")  # only first 6 chars for safety
