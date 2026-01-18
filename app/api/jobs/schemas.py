from typing import Literal

from pydantic import BaseModel, Field

from ...custom_types import JobParserStage
from ...models import EmailAuth, PhoneAuth


class JobSubmitEmailRequest(EmailAuth):
    search_query: str = Field(
        default="system analyst", max_length=200, min_length=1
    )
    max_applications: int = Field(default=200, ge=1, le=200)


class JobSubmitPhoneRequest(PhoneAuth):
    search_query: str = Field(
        default="system analyst", max_length=200, min_length=1
    )
    max_applications: int = Field(default=200, ge=1, le=200)


class JobSubmitResponse(BaseModel):
    task_id: str
    status: Literal["submitted"] = "submitted"
    check_status_url: str

    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "abc-123-def-456",
                "status": "submitted",
                "check_status_url": "/api/jobs/abc-123-def-456",
            }
        }


class JobStatusResponse(BaseModel):
    task_id: str
    state: str
    progress: float | None = None
    stage: JobParserStage | None = None
    applied: int | None = None
    total: int | None = None
    error: str | None = None
    result: dict | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "abc-123-def-456",
                "state": "PROGRESS",
                "progress": 45.5,
                "stage": "apply",
                "applied": 91,
                "total": 200,
            }
        }


class JobCancelResponse(BaseModel):
    task_id: str
    status: Literal["cancelled", "finished"] = "cancelled"
    message: str = "Task cancelled"

    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "abc-123-def-456",
                "status": "cancelled",
                "message": "Task cancelled",
            }
        }


class ErrorResponse(BaseModel):
    detail: str

    class Config:
        json_schema_extra = {"example": {"detail": "Task not found"}}
