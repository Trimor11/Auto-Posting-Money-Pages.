from datetime import datetime
from enum import Enum

from sqlalchemy import JSON, Column, DateTime, Enum as SqlEnum, ForeignKey, Integer, String, Text

from app.database import Base


class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class GenerationJob(Base):
    __tablename__ = "generation_jobs"

    id = Column(Integer, primary_key=True)
    keyword_id = Column(Integer, ForeignKey("keywords.id"), nullable=False)
    status = Column(SqlEnum(JobStatus), default=JobStatus.QUEUED)
    prompt_name = Column(String(60), nullable=False)
    model_name = Column(String(60), nullable=True)
    payload = Column(JSON, nullable=True)
    response = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    requested_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)


class PublishJob(Base):
    __tablename__ = "publish_jobs"

    id = Column(Integer, primary_key=True)
    page_id = Column(Integer, ForeignKey("pages.id"), nullable=False)
    status = Column(SqlEnum(JobStatus), default=JobStatus.QUEUED)
    scheduled_for = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
