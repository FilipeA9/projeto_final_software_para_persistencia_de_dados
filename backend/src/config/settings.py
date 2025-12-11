"""
Application settings and configuration management.

Loads environment variables and provides typed configuration objects.
"""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Configuration
    API_V1_PREFIX: str = "/api"
    API_TITLE: str = "Turistando API"
    API_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ALLOWED_ORIGINS: str = "http://localhost:8501,http://localhost:3000"

    # Database - PostgreSQL
    DATABASE_URL: str

    # Database - MongoDB
    MONGODB_URL: str
    MONGODB_DATABASE: str = "turistando_db"

    # Database - Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: str = ""
    REDIS_TTL: int = 300

    # JWT Authentication
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 24

    # File Upload
    UPLOAD_DIR: str = "uploads"
    MAX_PHOTO_SIZE_MB: int = 5
    MAX_PHOTOS_PER_SPOT: int = 10
    THUMBNAIL_SIZE: int = 300
    ALLOWED_EXTENSIONS: str = "jpg,jpeg,png,webp"

    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # Cache TTL (seconds)
    CACHE_SPOT_DETAILS_TTL: int = 300
    CACHE_SPOT_LIST_TTL: int = 60

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse comma-separated ALLOWED_ORIGINS into a list."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    @property
    def allowed_extensions_list(self) -> List[str]:
        """Parse comma-separated ALLOWED_EXTENSIONS into a list."""
        return [ext.strip() for ext in self.ALLOWED_EXTENSIONS.split(",")]

    @property
    def max_photo_size_bytes(self) -> int:
        """Convert MAX_PHOTO_SIZE_MB to bytes."""
        return self.MAX_PHOTO_SIZE_MB * 1024 * 1024


# Global settings instance
settings = Settings()
