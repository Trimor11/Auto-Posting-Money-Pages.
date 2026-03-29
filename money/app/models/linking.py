from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String

from app.database import Base


class InternalLink(Base):
    __tablename__ = "internal_links"

    id = Column(Integer, primary_key=True)
    from_page_id = Column(Integer, ForeignKey("pages.id"), nullable=False)
    to_page_id = Column(Integer, ForeignKey("pages.id"), nullable=False)
    anchor_text = Column(String(255), nullable=False)
    relevance_score = Column(Float, default=0.5)
    created_at = Column(DateTime, default=datetime.utcnow)
