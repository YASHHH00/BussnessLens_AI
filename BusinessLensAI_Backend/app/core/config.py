"""
BusinessLens AI Backend — Application Configuration

All configuration is loaded from environment variables (12-factor app).
No secrets, no hardcoded values. Use .env for local development.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import AnyUrl, Field, PostgresDsn, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central configuration class.
    Every field is loaded from an environment variable of the same name (case-insensitive).
    Pydantic-settings handles type coercion and validation automatically.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Silently ignore unexpected env vars
    )

    # ------------------------------------------------------------------ #
    # Application
    # ------------------------------------------------------------------ #
    APP_NAME: str = "BusinessLens AI"
    APP_ENV: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = False
    API_PREFIX: str = "/api/v1"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1

    # ------------------------------------------------------------------ #
    # Database (application / metadata DB)
    # ------------------------------------------------------------------ #
    DATABASE_URL: str = Field(..., description="Async PostgreSQL DSN (asyncpg driver)")

    # Pool settings for production
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    DB_ECHO: bool = False  # Set True only for debug SQL logging

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if not v.startswith(("postgresql+asyncpg://", "sqlite+aiosqlite://")):
            raise ValueError(
                "DATABASE_URL must use asyncpg driver: "
                "postgresql+asyncpg://user:pass@host:port/db"
            )
        return v

    # ------------------------------------------------------------------ #
    # Security — JWT
    # ------------------------------------------------------------------ #
    SECRET_KEY: str = Field(..., min_length=32, description="JWT signing secret")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ------------------------------------------------------------------ #
    # Security — Fernet (credential encryption at rest)
    # ------------------------------------------------------------------ #
    FERNET_KEY: str = Field(
        ...,
        description=(
            "Fernet symmetric key for encrypting DB credentials at rest. "
            "Generate: python -c \"from cryptography.fernet import Fernet; "
            "print(Fernet.generate_key().decode())\""
        ),
    )

    # ------------------------------------------------------------------ #
    # CORS
    # ------------------------------------------------------------------ #
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    @property
    def allowed_origins_list(self) -> list[str]:
        """Parse comma-separated CORS origins into a list."""
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

    # ------------------------------------------------------------------ #
    # Account Security
    # ------------------------------------------------------------------ #
    MAX_FAILED_LOGIN_ATTEMPTS: int = 5
    ACCOUNT_LOCKOUT_MINUTES: int = 15

    # ------------------------------------------------------------------ #
    # Rate Limiting
    # ------------------------------------------------------------------ #
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_LOGIN_PER_MINUTE: int = 5
    RATE_LIMIT_AI_PER_MINUTE: int = 20
    RATE_LIMIT_GLOBAL_PER_MINUTE: int = 100

    # ------------------------------------------------------------------ #
    # AI Providers
    # ------------------------------------------------------------------ #
    AI_PROVIDER: Literal["gemini", "openai"] = "gemini"
    GEMINI_API_KEY: str | None = None
    OPENAI_API_KEY: str | None = None
    AI_REQUEST_TIMEOUT_SECONDS: int = 30
    AI_MAX_RETRIES: int = 2
    AI_COST_OPTIMIZATION_ENABLED: bool = True

    # Confidence threshold: >= this → preselect mapping (NOT auto-accept — still requires user confirmation)
    AI_CONFIDENCE_PRESELECT_THRESHOLD: float = Field(0.95, ge=0.0, le=1.0)

    @model_validator(mode="after")
    def validate_ai_provider_key(self) -> "Settings":
        """Warn if the selected AI provider has no API key (don't hard-fail — allows startup)."""
        if self.AI_PROVIDER == "gemini" and not self.GEMINI_API_KEY:
            import warnings
            warnings.warn(
                "AI_PROVIDER=gemini but GEMINI_API_KEY is not set. "
                "AI features will be unavailable.",
                stacklevel=2,
            )
        if self.AI_PROVIDER == "openai" and not self.OPENAI_API_KEY:
            import warnings
            warnings.warn(
                "AI_PROVIDER=openai but OPENAI_API_KEY is not set. "
                "AI features will be unavailable.",
                stacklevel=2,
            )
        return self

    # ------------------------------------------------------------------ #
    # Domain Plugin
    # ------------------------------------------------------------------ #
    ACTIVE_DOMAIN_PLUGIN: str = "retail"

    # ------------------------------------------------------------------ #
    # Forecasting
    # ------------------------------------------------------------------ #
    FORECAST_PROVIDER: Literal["statsforecast", "sklearn"] = "statsforecast"
    FORECAST_MIN_DATA_POINTS: int = 30

    # ------------------------------------------------------------------ #
    # Cache Layer
    # ------------------------------------------------------------------ #
    CACHE_PROVIDER: Literal["redis", "memory"] = "memory"
    REDIS_URL: str | None = None
    CACHE_DEFAULT_TTL_SECONDS: int = 300          # 5 min
    CACHE_DASHBOARD_TTL_SECONDS: int = 120         # 2 min
    CACHE_KPI_TTL_SECONDS: int = 180              # 3 min
    CACHE_SCHEMA_ANALYSIS_TTL_SECONDS: int = 3600  # 1 hour

    @model_validator(mode="after")
    def validate_redis_url(self) -> "Settings":
        if self.CACHE_PROVIDER == "redis" and not self.REDIS_URL:
            import warnings
            warnings.warn(
                "CACHE_PROVIDER=redis but REDIS_URL is not set. "
                "Falling back to in-memory cache.",
                stacklevel=2,
            )
        return self

    # ------------------------------------------------------------------ #
    # Analytics Engine
    # ------------------------------------------------------------------ #
    QUERY_TIMEOUT_SECONDS: int = 30
    QUERY_ROW_CAP: int = 10_000

    # ------------------------------------------------------------------ #
    # SQL Playground
    # ------------------------------------------------------------------ #
    SQL_PLAYGROUND_ENABLED: bool = True
    SQL_PLAYGROUND_MAX_TIMEOUT_SECONDS: int = 30
    SQL_PLAYGROUND_MAX_ROWS: int = 10_000

    # ------------------------------------------------------------------ #
    # File Uploads
    # ------------------------------------------------------------------ #
    MAX_UPLOAD_SIZE_MB: int = 50

    @property
    def max_upload_size_bytes(self) -> int:
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    # ------------------------------------------------------------------ #
    # Audit Log
    # ------------------------------------------------------------------ #
    AUDIT_LOG_ENABLED: bool = True

    # ------------------------------------------------------------------ #
    # Dashboard Themes
    # ------------------------------------------------------------------ #
    DASHBOARD_DEFAULT_THEME: Literal["dark", "light", "system"] = "system"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Return the singleton Settings instance.
    Cached after first call — safe to call from anywhere.
    Import and call this function; do not import Settings directly in services.
    """
    return Settings()


# Convenience alias used throughout the app
settings = get_settings()
