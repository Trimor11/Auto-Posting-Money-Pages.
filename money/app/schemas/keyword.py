from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.keyword import KeywordStatus


class KeywordBase(BaseModel):
    phrase: str
    category_id: Optional[int] = None
    priority_score: Optional[float] = 0
    search_intent: Optional[str] = "informational"
    country: Optional[str] = "global"
    language: Optional[str] = "en"
    source: Optional[str] = "manual"
    topic_family: Optional[str] = None
    target_page_type: Optional[str] = None
    notes: Optional[str] = None


class KeywordCreate(KeywordBase):
    ...


class KeywordOut(KeywordBase):
    id: int
    slug: str
    status: KeywordStatus
    created_at: datetime

    class Config:
        orm_mode = True
