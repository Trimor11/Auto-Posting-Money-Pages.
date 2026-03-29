from pydantic import BaseModel


class SettingUpdate(BaseModel):
    site_name: str
    default_language: str = "en"
    default_country: str = "global"
    ads_top_code: str | None = None
    ads_mid_code: str | None = None
    ads_bottom_code: str | None = None
    affiliate_block_html: str | None = None
    analytics_snippet: str | None = None
    daily_generation_quota: int = 5
    daily_publish_quota: int = 5
    max_pages_per_day: int = 12
    dry_run_mode: bool = False
