from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from app.database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String(120), unique=True, nullable=False)
    slug = Column(String(160), unique=True, nullable=False)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
