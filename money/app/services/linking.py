import random
from typing import List

from sqlalchemy.orm import Session

from app.models import InternalLink, Page, PageStatus


def suggest_links(db: Session, page: Page, limit: int = 5) -> List[InternalLink]:
    candidates = (
        db.query(Page)
        .filter(Page.id != page.id, Page.status == page.status)
        .filter(Page.category_id == page.category_id)
        .order_by(Page.published_at.desc())
        .limit(limit * 3)
        .all()
    )
    picked = random.sample(candidates, k=min(limit, len(candidates))) if candidates else []
    links: List[InternalLink] = []
    for target in picked:
        anchor = target.title.split(" ")[:5]
        anchor_text = " ".join(anchor)
        links.append(
            InternalLink(
                from_page_id=page.id,
                to_page_id=target.id,
                anchor_text=anchor_text,
                relevance_score=0.7,
            )
        )
    return links


def persist_links(db: Session, links: List[InternalLink]) -> None:
    for link in links:
        exists = (
            db.query(InternalLink)
            .filter(
                InternalLink.from_page_id == link.from_page_id,
                InternalLink.to_page_id == link.to_page_id,
            )
            .first()
        )
        if exists:
            continue
        db.add(link)
    # Commit handled by caller


def refresh_link_graph(db: Session, per_page: int = 3) -> None:
    pages = (
        db.query(Page)
        .filter(Page.status == PageStatus.PUBLISHED)
        .order_by(Page.updated_at.desc())
        .limit(50)
        .all()
    )
    for page in pages:
        current = (
            db.query(InternalLink)
            .filter(InternalLink.from_page_id == page.id)
            .count()
        )
        if current >= per_page:
            continue
        links = suggest_links(db, page, limit=per_page - current)
        persist_links(db, links)
    db.commit()
