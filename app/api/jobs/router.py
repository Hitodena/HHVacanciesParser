from celery.result import AsyncResult
from fastapi import APIRouter, Request
from loguru import logger

from ...celery_app.tasks.parsing_tasks import process_job_application
from ...custom_types import JobParserStage
from ...models import EmailAuth, PhoneAuth
from ..dependencies import CeleryDep
from .exceptions import TaskNotFoundException
from .schemas import (
    ErrorResponse,
    JobCancelResponse,
    JobStatusResponse,
    JobSubmitEmailRequest,
    JobSubmitPhoneRequest,
    JobSubmitResponse,
)

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post(
    "/submit/email",
    response_model=JobSubmitResponse,
    status_code=201,
    summary="Submit job task (email authentication)",
    responses={
        201: {"description": "Task successfully submitted"},
        400: {"model": ErrorResponse},
    },
)
async def submit_job_email(
    data: JobSubmitEmailRequest,
    request: Request,
    celery: CeleryDep,
):
    """
    Submits a job application automation task with email authentication.

    The request body should contain:
    - **email**: Email for login on hh.ru
    - **password**: Account password
    - **search_query**: Search query (e.g., "python developer")
    - **max_applications**: Maximum number of applications (1-200)

    Returns:
    - task_id for tracking progress
    - URL for checking status
    """

    logger.bind(search_query=data.search_query, type="email").info(
        "Received parsing request"
    )

    # Create credentials for Celery
    credentials = EmailAuth(email=data.email, password=data.password)

    # Send task
    task = process_job_application.delay(  # type:ignore
        credentials=credentials.model_dump_json(),
        search_query=data.search_query,
        max_applications=data.max_applications,
    )

    logger.bind(task_id=task.id).info("Task sent to queue")

    return JobSubmitResponse(
        task_id=task.id,
        check_status_url=str(
            request.url_for("get_job_status", task_id=task.id)
        ),
    )


@router.post(
    "/submit/phone",
    response_model=JobSubmitResponse,
    status_code=201,
    summary="Submit job task (phone authentication)",
    responses={
        201: {"description": "Task successfully submitted"},
        400: {"model": ErrorResponse},
    },
)
async def submit_job_phone(
    data: JobSubmitPhoneRequest,
    request: Request,
    celery: CeleryDep,
):
    """
    Submits a job application automation task with phone authentication.

    The request body should contain:
    - **phone**: Phone number (without country code)
    - **country**: Country (Russia, Belarus, etc.)
    - **password**: Account password
    - **search_query**: Search query
    - **max_applications**: Maximum number of applications (1-200)

    Returns:
    - task_id for tracking progress
    - URL for checking status
    """

    logger.bind(search_query=data.search_query, type="phone").info(
        "Received parsing request"
    )

    # Create credentials for Celery
    credentials = PhoneAuth(
        phone=data.phone, country=data.country, password=data.password
    )

    # Send task
    task = process_job_application.delay(  # type: ignore
        credentials=credentials.model_dump_json(),
        search_query=data.search_query,
        max_applications=data.max_applications,
    )

    logger.bind(task_id=task.id).info("Task sent to queue")

    return JobSubmitResponse(
        task_id=task.id,
        check_status_url=str(
            request.url_for("get_job_status", task_id=task.id)
        ),
    )


@router.get(
    "/{task_id}",
    response_model=JobStatusResponse,
    summary="Get task status",
    responses={
        200: {"description": "Task status"},
        404: {"model": ErrorResponse, "description": "Task not found"},
    },
)
async def get_job_status(task_id: str, celery: CeleryDep):
    """
    Gets the current execution status of the task.

    **States:**
    - **PENDING**: Task in queue
    - **PROGRESS**: Executing (contains progress, stage, applied, total)
    - **SUCCESS**: Completed successfully
    - **FAILURE**: Execution error

    **Returns:**
    - Current status and execution progress
    """

    result = AsyncResult(task_id, app=celery)

    # Base response
    response = JobStatusResponse(task_id=task_id, state=result.state)

    if result.state == "PENDING":
        response.progress = 0.0

    if result.state == "PROGRESS":
        # Celery task.update_state(meta={...})
        info = result.info or {}
        response.progress = info.get("progress", 0.0)
        response.stage = info.get("stage")
        response.applied = info.get("applied")
        response.total = info.get("total")

    elif result.state == "SUCCESS":
        response.result = result.result
        response.progress = result.result.get("progress")
        response.applied = result.result.get("applied")
        response.total = result.result.get("total")
        response.stage = JobParserStage.COMPLETE

    elif result.state == "FAILURE":
        response.error = str(result.info)

    return response


@router.post(
    "/{task_id}/cancel",
    response_model=JobCancelResponse,
    summary="Cancel task",
    responses={
        200: {"description": "Task cancelled"},
        404: {"model": ErrorResponse, "description": "Task not found"},
    },
)
async def cancel_job(task_id: str, celery: CeleryDep):
    """
    Cancels task execution.

    **Warning:**
    - If the task is already running, it will be forcibly stopped (SIGKILL)
    - Browser will be closed
    - Partial results will be lost

    **Returns:**
    - Cancellation confirmation
    """

    result = AsyncResult(task_id, app=celery)

    # Check task existence
    if result.state == "PENDING" and not result.info:
        raise TaskNotFoundException(task_id)

    # Cancel task
    celery.control.revoke(task_id, terminate=True)

    logger.bind(task_id=task_id).warning("Task cancelled")

    return JobCancelResponse(task_id=task_id)
