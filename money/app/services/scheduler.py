from datetime import datetime, timedelta
from typing import List

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app import dependencies
from app.config import get_settings
from app.database import SessionLocal
from app.models import Keyword, KeywordStatus, Page, PageStatus
from app.services.content_engine import ContentEngine
from app.services.publisher import publish_ready_pages, rebuild_sitemap_cache, run_publish_jobs
from app.services import linking

settings = get_settings()
scheduler = AsyncIOScheduler(timezone=settings.scheduler_timezone)


def _with_db(func):
    def wrapper(*args, **kwargs):
        db = SessionLocal()
        try:
            return func(db=db, *args, **kwargs)
        finally:
            db.close()

    return wrapper


@_with_db
def generate_batch(db, limit: int = None):
    if settings.dry_run_mode:
        return
    runtime = dependencies.build_runtime_settings(db)
    limit = limit or runtime.daily_generation_quota
    keywords: List[Keyword] = (
        db.query(Keyword)
        .filter(Keyword.status.in_([KeywordStatus.QUEUED, KeywordStatus.IDEA]))
        .order_by(Keyword.priority_score.desc(), Keyword.created_at.asc())
        .limit(limit)
        .all()
    )
    engine = ContentEngine(db)
    for keyword in keywords:
        try:
            engine.generate_page(keyword)
        except Exception:
            keyword.status = KeywordStatus.FAILED
            db.commit()


@_with_db
def publish_batch(db, limit: int = None):
    runtime = dependencies.build_runtime_settings(db)
    limit = limit or runtime.daily_publish_quota
    publish_ready_pages(db, limit, dry_run=settings.dry_run_mode)
    run_publish_jobs(db, limit, dry_run=settings.dry_run_mode)
    rebuild_sitemap_cache(db)


@_with_db
def mark_stale_pages(db, days: int = 45):
    threshold = datetime.utcnow() - timedelta(days=days)
    pages = (
        db.query(Page)
        .filter(Page.status == PageStatus.PUBLISHED, Page.updated_at < threshold)
        .all()
    )
    for page in pages:
        page.status = PageStatus.REVIEW
        db.add(page)
    db.commit()


@_with_db
def refresh_links(db):
    linking.refresh_link_graph(db)


def start_scheduler():
    if not settings.scheduler_enabled:
        return
    if not scheduler.running:
        scheduler.add_job(generate_batch, "cron", hour=1, id="generate_daily")
        scheduler.add_job(publish_batch, "cron", hour=2, id="publish_daily")
        scheduler.add_job(mark_stale_pages, "cron", hour=3, id="stale_flag")
        scheduler.add_job(refresh_links, "cron", hour=4, id="link_refresh")
        scheduler.start()


def shutdown_scheduler():
    if scheduler.running:
        scheduler.shutdown()
