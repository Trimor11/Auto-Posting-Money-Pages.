from datetime import datetime
from enum import Enum

from sqlalchemy import JSON, Boolean, Column, DateTime, Enum as SqlEnum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class PageStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    SCHEDULED = "scheduled"
    REVIEW = "review"
    ARCHIVED = "archived"


class Page(Base):
    __tablename__ = "pages"

    id = Column(Integer, primary_key=True)
    keyword_id = Column(Integer, ForeignKey("keywords.id"), nullable=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    slug = Column(String(255), unique=True, nullable=False)
    title = Column(String(255), nullable=False)
    meta_title = Column(String(255), nullable=False)
    meta_description = Column(String(255), nullable=False)
    h1 = Column(String(255), nullable=False)
    summary = Column(Text, nullable=True)
    intro = Column(Text, nullable=True)
    body_json = Column(JSON, nullable=False)
    faq_json = Column(JSON, nullable=True)
    schema_json = Column(JSON, nullable=True)
    related_topics = Column(JSON, nullable=True)
    page_type = Column(String(60), nullable=False)
    status = Column(SqlEnum(PageStatus), default=PageStatus.DRAFT)
    canonical_url = Column(String(255), nullable=True)
    language = Column(String(8), default="en")
    country_target = Column(String(8), default="global")
    word_count = Column(Integer, default=0)
    reading_time = Column(Integer, default=1)
    quality_score = Column(Integer, default=80)
    featured = Column(Boolean, default=False)
    noindex = Column(Boolean, default=False)
    ads_enabled = Column(Boolean, default=True)
    author_name = Column(String(120), default="Editorial Team")
    cta_text = Column(String(255), nullable=True)
    affiliate_block = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    publish_at = Column(DateTime, nullable=True)
    published_at = Column(DateTime, nullable=True)

    keyword = relationship("Keyword", back_populates="page")
    category = relationship("Category")
