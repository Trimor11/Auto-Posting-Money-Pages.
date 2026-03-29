from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.database import get_db
from app.models import User
from app.services.settings_service import SettingsService
from app.utils.security import decode_session_token


def get_settings_dep() -> Settings:
    return get_settings()


def get_db_dep() -> Session:
    yield from get_db()


def get_current_user(
    request: Request,
    db: Session = Depends(get_db_dep),
    settings: Settings = Depends(get_settings_dep),
) -> User:
    token = request.cookies.get(settings.session_cookie_name)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    user_id = decode_session_token(token, settings.secret_key)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return user


def build_runtime_settings(db: Session) -> Settings:
    base = get_settings()
    runtime = Settings(**base.dict())
    service = SettingsService(db)
    runtime.ads_top_code = service.get("ads_top_code", base.ads_top_code)
    runtime.ads_mid_code = service.get("ads_mid_code", base.ads_mid_code)
    runtime.ads_bottom_code = service.get("ads_bottom_code", base.ads_bottom_code)
    runtime.affiliate_block_html = service.get("affiliate_block_html", base.affiliate_block_html)
    runtime.analytics_snippet = service.get("analytics_snippet", base.analytics_snippet)
    runtime.daily_generation_quota = int(service.get("daily_generation_quota", base.daily_generation_quota))
    runtime.daily_publish_quota = int(service.get("daily_publish_quota", base.daily_publish_quota))
    return runtime


def get_runtime_settings(
    db: Session = Depends(get_db_dep),
) -> Settings:
    return build_runtime_settings(db)
