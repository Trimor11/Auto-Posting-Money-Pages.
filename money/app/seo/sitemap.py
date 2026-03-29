from datetime import datetime
from typing import List
from xml.etree.ElementTree import Element, SubElement, tostring

from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import Page, PageStatus

settings = get_settings()


def build_sitemap(db: Session) -> str:
    pages: List[Page] = (
        db.query(Page)
        .filter(Page.status == PageStatus.PUBLISHED, Page.noindex.is_(False))
        .order_by(Page.updated_at.desc())
        .all()
    )
    urlset = Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    for page in pages:
        url = SubElement(urlset, "url")
        loc = SubElement(url, "loc")
        loc.text = f"{settings.site_url}/{page.slug}"
        lastmod = SubElement(url, "lastmod")
        lastmod.text = (page.updated_at or datetime.utcnow()).date().isoformat()
        changefreq = SubElement(url, "changefreq")
        changefreq.text = "weekly"
        priority = SubElement(url, "priority")
        priority.text = "0.6"
    return tostring(urlset, encoding="utf-8", xml_declaration=True).decode()
