import asyncio

from celery import Task
from loguru import logger

from ...custom_types import JobParserStage
from ...models import AuthCredentials, JobSearchResult
from ...services import process_job_search
from ..celery_app import celery_app
from ..worker_context import get_worker_context


class CallbackTask(Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error(f" Task {task_id} failed: {exc}")


@celery_app.task(
    bind=True, base=CallbackTask, name="process_job_application", pydantic=True
)
def process_job_application(
    self,
    credentials: AuthCredentials,
    search_query: str,
    max_applications: int = 200,
) -> JobSearchResult:
    """
    Celery task for automating applications on hh.ru

    Args:
        credentials: EmailAuth or PhoneAuth model
        search_query: Search query
        max_applications: Maximum applications
    """
    return asyncio.run(
        _process_async(self, credentials, search_query, max_applications)
    )


async def _process_async(
    task,
    credentials: AuthCredentials,
    search_query: str,
    max_applications: int,
) -> JobSearchResult:
    """Asynchronous task processing"""

    # Get context
    context = get_worker_context()

    # Callback for updating progress
    def progress_callback(
        stage: JobParserStage, progress: float, **kwargs
    ) -> None:
        task.update_state(
            state="PROGRESS",
            meta={"stage": stage, "progress": progress, **kwargs},
        )

    # Create browser context for this task
    if not context.browser_manager:
        raise RuntimeError("Worker browser is not initialized")
    async with context.browser_manager.context() as page:
        logger.bind(
            search_query=search_query, max_applications=max_applications
        ).info("Celery HHJob starting processing")

        # Launch main workflow
        if not context.config:
            raise RuntimeError("Worker config is not initialized")
        result = await process_job_search(
            page=page,
            config=context.config,
            credentials=credentials,
            search_query=search_query,
            max_applications=max_applications,
            progress_callback=progress_callback,
        )

        logger.bind(
            result_applied=result.applied,
            result_total=result.total,
            result_status=result.status,
        ).success("Celery HHJob Completed")

        return result
