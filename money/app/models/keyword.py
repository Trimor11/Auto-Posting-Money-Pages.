from datetime import datetime
from enum import Enum

from sqlalchemy import Column, DateTime, Enum as SqlEnum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class KeywordStatus(str, Enum):
    IDEA = "idea"
    QUEUED = "queued"
    GENERATING = "generating"
    DRAFT = "draft"
    PUBLISHED = "published"
    FAILED = "failed"
    ARCHIVED = "archived"


class Keyword(Base):
    __tablename__ = "keywords"

    id = Column(Integer, primary_key=True)
    phrase = Column(String(255), nullable=False, unique=True)
    slug = Column(String(255), nullable=False, unique=True)
    status = Column(SqlEnum(KeywordStatus), default=KeywordStatus.IDEA, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    search_intent = Column(String(50), default="informational")
    priority_score = Column(Numeric(5, 2), default=0)
    country = Column(String(8), default="global")
    language = Column(String(8), default="en")
    source = Column(String(50), default="manual")
    topic_family = Column(String(120), nullable=True)
    target_page_type = Column(String(60), nullable=True)
    dedup_hash = Column(String(64), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_generated_at = Column(DateTime, nullable=True)

    category = relationship("Category")
    page = relationship("Page", back_populates="keyword", uselist=False)
