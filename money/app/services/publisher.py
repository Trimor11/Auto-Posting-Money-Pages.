from datetime import datetime
from pathlib import Path
from typing import Iterable, List

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import JobStatus, Page, PageStatus, PublishJob
from app.seo.sitemap import build_sitemap
from app.services import linking

settings = get_settings()
CACHE_SITEMAP_PATH = Path("./generated_sitemap.xml")


def publish_ready_pages(db: Session, limit: int, dry_run: bool = False) -> List[Page]:
    pages: List[Page] = (
        db.query(Page)
        .filter(
            Page.status == PageStatus.DRAFT,
            or_(Page.publish_at.is_(None), Page.publish_at <= datetime.utcnow()),
        )
        .order_by(Page.publish_at.asc())
        .limit(limit)
        .all()
    )
    published: List[Page] = []
    for page in pages:
        if dry_run:
            continue
        page.status = PageStatus.PUBLISHED
        page.published_at = datetime.utcnow()
        page.updated_at = datetime.utcnow()
        db.add(page)
        links = linking.suggest_links(db, page)
        linking.persist_links(db, links)
        published.append(page)
    if not dry_run:
        db.commit()
    return published


def run_publish_jobs(db: Session, limit: int, dry_run: bool = False) -> int:
    jobs: List[PublishJob] = (
        db.query(PublishJob)
        .filter(PublishJob.status == JobStatus.QUEUED)
        .order_by(PublishJob.scheduled_for.asc())
        .limit(limit)
        .all()
    )
    for job in jobs:
        job.started_at = datetime.utcnow()
        job.status = JobStatus.RUNNING
        db.add(job)
        if dry_run:
            job.status = JobStatus.SKIPPED
            continue
        page = db.query(Page).filter(Page.id == job.page_id).first()
        if not page:
            job.status = JobStatus.FAILED
            job.error_message = "Missing page"
            continue
        page.status = PageStatus.PUBLISHED
        page.published_at = datetime.utcnow()
        job.status = JobStatus.SUCCESS
        job.completed_at = datetime.utcnow()
    db.commit()
    return len(jobs)


def rebuild_sitemap_cache(db: Session) -> Path:
    xml = build_sitemap(db)
    CACHE_SITEMAP_PATH.write_text(xml, encoding="utf-8")
    return CACHE_SITEMAP_PATH


def latest_sitemap() -> str:
    if CACHE_SITEMAP_PATH.exists():
        return CACHE_SITEMAP_PATH.read_text(encoding="utf-8")
    return ""
