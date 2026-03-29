from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import GenerationJob, JobStatus, Keyword, KeywordStatus, Page, PageStatus
from app.services.ai_provider import load_provider
from app.services.ai_templates import get_template
from app.services.quality import evaluate_content
from app.utils.slug import ensure_unique_slug, slugify
from app.utils.text import reading_time_minutes, word_count

settings = get_settings()
provider = load_provider(settings)


class ContentEngine:
    def __init__(self, db: Session):
        self.db = db

    def generate_page(self, keyword: Keyword, force: bool = False) -> Page:
        template = get_template(keyword.target_page_type or "explanation")
        job = GenerationJob(
            keyword_id=keyword.id,
            status=JobStatus.RUNNING,
            prompt_name=template.page_type,
            model_name=settings.ai_model,
            requested_at=datetime.utcnow(),
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)

        keyword.status = KeywordStatus.GENERATING
        self.db.commit()

        extras = {
            "intent": keyword.search_intent,
            "category": keyword.topic_family or "General",
            "audience": "self-serve creator",
            "related": [keyword.phrase, f"{keyword.phrase} basics"],
        }
        job.payload = extras
        self.db.commit()
        try:
            payload = provider.generate(template, keyword.phrase, extras)
        except Exception as exc:  # pragma: no cover - runtime safety
            keyword.status = KeywordStatus.FAILED
            job.status = JobStatus.FAILED
            job.error_message = str(exc)
            self.db.commit()
            raise

        job.response = payload
        job.completed_at = datetime.utcnow()

        sections = payload.get("sections", [])
        faq = payload.get("faq", [])
        rendered_body = " ".join(section.get("body", "") for section in sections)
        meta_title = payload.get("seo_title") or keyword.phrase.title()
        slug_candidate = slugify(payload.get("slug") or keyword.slug)
        page = self.db.query(Page).filter(Page.keyword_id == keyword.id).first()
        existing_slugs = {row[0] for row in self.db.query(Page.slug).all()}
        existing_titles = {row[0] for row in self.db.query(Page.title).all()}
        if page:
            existing_slugs.discard(page.slug)
            existing_titles.discard(page.title)
        slug = ensure_unique_slug(slug_candidate, existing_slugs)
        report = evaluate_content(rendered_body, len(faq), meta_title, slug, existing_titles, existing_slugs)

        if not report.passed and not force:
            keyword.status = KeywordStatus.FAILED
            job.status = JobStatus.FAILED
            job.error_message = "; ".join(issue.message for issue in report.issues)
            self.db.commit()
            raise ValueError(job.error_message)

        if not page:
            page = Page(keyword_id=keyword.id)
        page.slug = slug
        page.title = meta_title
        page.meta_title = meta_title
        page.meta_description = payload.get("meta_description") or rendered_body[:150]
        page.h1 = payload.get("h1") or keyword.phrase.title()
        page.summary = payload.get("summary")
        page.intro = payload.get("intro")
        page.body_json = sections
        page.faq_json = faq
        page.schema_json = payload.get("schema")
        page.related_topics = payload.get("related_topics", [])
        page.page_type = template.page_type
        page.category_id = keyword.category_id
        page.status = PageStatus.DRAFT
        page.word_count = word_count(rendered_body)
        page.reading_time = reading_time_minutes(rendered_body)
        page.cta_text = payload.get("callouts", [{}])[0].get("body") if payload.get("callouts") else None
        page.canonical_url = f"{settings.site_url}/{slug}"
        page.publish_at = datetime.utcnow()
        page.updated_at = datetime.utcnow()
        page.language = keyword.language
        page.country_target = keyword.country
        page.quality_score = min(100, 70 + report.words // 10)
        page.noindex = False
        page.author_name = "Editorial Bot"

        keyword.status = KeywordStatus.DRAFT
        keyword.last_generated_at = datetime.utcnow()
        job.status = JobStatus.SUCCESS

        self.db.add(page)
        self.db.commit()
        self.db.refresh(page)
        return page

    def regenerate_section(self, page: Page, section_name: str) -> Page:
        sections: List[Dict] = page.body_json or []
        for section in sections:
            if section["title"].lower().startswith(section_name.lower()):
                section["body"] = section["body"] + "\n<p>Updated for freshness.</p>"
        page.body_json = sections
        page.updated_at = datetime.utcnow()
        self.db.add(page)
        self.db.commit()
        return page
