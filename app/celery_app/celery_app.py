import asyncio

from celery import Celery
from celery.signals import (
    worker_process_init,
    worker_process_shutdown,
)
from loguru import logger

from ..core import load
from .worker_context import WorkerContext

config = load()

celery_app = Celery(
    "HHAutoApply",
    broker=config.environment.celery_broker_url,
    backend=config.environment.celery_result_backend,
    include=["app.celery_app.tasks.parsing_tasks"],
)


celery_app.config_from_object("app.celery_app.celery_config:CeleryConfig")


@worker_process_init.connect
def init_worker(**kwargs):
    """Called once at the start of each worker process"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.run_until_complete(WorkerContext.init())


@worker_process_shutdown.connect
def shutdown_worker(**kwargs):
    """Called once at the end of each worker process"""
    context = WorkerContext._instance
    if context:
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            loop.run_until_complete(context.cleanup())
        except Exception as e:
            logger.error(f"Error during worker shutdown: {e}")

