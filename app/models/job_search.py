from pydantic import BaseModel, Field

from ..custom_types import JobSearchStatus


class JobSearchResult(BaseModel):
    status: JobSearchStatus
    applied: int
    total: int = 0
    progress: float = Field(0, le=100, ge=0)  # Percentage 0-100
    message: str | None = None
