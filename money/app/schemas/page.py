from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel

from app.models.page import PageStatus


class Section(BaseModel):
    heading: str
    body: str


class FAQItem(BaseModel):
    question: str
    answer: str


class PageBase(BaseModel):
    title: str
    meta_title: str
    meta_description: str
    h1: str
    summary: Optional[str]
    intro: Optional[str]
    sections: List[Section] = []
    faq: List[FAQItem] = []
    page_type: str
    language: str = "en"
    country_target: str = "global"
    cta_text: Optional[str] = None
    noindex: bool = False


class PageOut(PageBase):
    id: int
    slug: str
    status: PageStatus
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime]

    class Config:
        orm_mode = True


class PageRender(BaseModel):
    page: PageOut
    related_pages: List[PageOut] = []
    structured_data: Any = None
