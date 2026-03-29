from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel

from app.models.job import JobStatus


class JobOut(BaseModel):
    id: int
    status: JobStatus
    prompt_name: Optional[str]
    model_name: Optional[str]
    payload: Optional[Any]
    response: Optional[Any]
    error_message: Optional[str]
    requested_at: datetime
    completed_at: Optional[datetime]

    class Config:
        orm_mode = True
