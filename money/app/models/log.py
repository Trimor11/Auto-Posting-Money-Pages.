from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, String, Text

from app.database import Base


class LogEvent(Base):
    __tablename__ = "log_events"

    id = Column(String(36), primary_key=True)
    level = Column(String(20), default="INFO")
    message = Column(Text, nullable=False)
    context = Column(String(60), nullable=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
