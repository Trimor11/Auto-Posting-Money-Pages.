from functools import lru_cache
from pydantic import BaseSettings, Field, validator


class Settings(BaseSettings):
    """Runtime configuration for the Auto-Posting Money Pages platform."""

    project_name: str = "Auto-Posting Money Pages"
    environment: str = Field("development", env="ENVIRONMENT")
    secret_key: str = Field("change-me", env="SECRET_KEY")
    database_url: str = Field("sqlite:///./money.db", env="DATABASE_URL")
    site_url: str = Field("http://localhost:8000", env="SITE_URL")
    admin_email: str = Field("admin@example.com", env="ADMIN_EMAIL")
    admin_password: str = Field("admin123", env="ADMIN_PASSWORD")
    session_cookie_name: str = "apmp_admin"
    ai_provider: str = Field("openai", env="AI_PROVIDER")
    ai_model: str = Field("gpt-4o-mini", env="AI_MODEL")
    ai_temperature: float = Field(0.3, env="AI_TEMPERATURE")
    ai_max_tokens: int = Field(1800, env="AI_MAX_TOKENS")
    ai_timeout: int = Field(45, env="AI_TIMEOUT")
    ai_mock_mode: bool = Field(False, env="AI_MOCK_MODE")
    scheduler_timezone: str = Field("UTC", env="SCHEDULER_TIMEZONE")
    scheduler_enabled: bool = Field(True, env="SCHEDULER_ENABLED")
    daily_generation_quota: int = Field(5, env="DAILY_GENERATION_QUOTA")
    daily_publish_quota: int = Field(5, env="DAILY_PUBLISH_QUOTA")
    max_pages_per_day: int = Field(12, env="MAX_PAGES_PER_DAY")
    dry_run_mode: bool = Field(False, env="DRY_RUN_MODE")
    ads_top_code: str = Field("", env="ADS_TOP_CODE")
    ads_mid_code: str = Field("", env="ADS_MID_CODE")
    ads_bottom_code: str = Field("", env="ADS_BOTTOM_CODE")
    affiliate_block_html: str = Field("", env="AFFILIATE_BLOCK_HTML")
    analytics_snippet: str = Field("", env="ANALYTICS_SNIPPET")
    enable_rate_limiting: bool = Field(True, env="ENABLE_RATE_LIMITING")
    search_rate_limit_per_minute: int = Field(30, env="SEARCH_RATE_LIMIT")
    cache_sitemap_minutes: int = Field(30, env="CACHE_SITEMAP_MINUTES")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @validator("database_url")
    def _sqlite_path(cls, v: str) -> str:
        if v.startswith("sqlite") and "check_same_thread" not in v:
            connector = "?" if "?" not in v else "&"
            return f"{v}{connector}check_same_thread=False"
        return v


@lru_cache()
def get_settings() -> Settings:
    return Settings()
