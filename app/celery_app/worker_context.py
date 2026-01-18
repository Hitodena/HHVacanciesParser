from typing import Optional

from loguru import logger

from ..core import Config, load
from ..services import BrowserManager


class WorkerContext:
    """Celery worker context"""

    _instance: Optional["WorkerContext"] = None

    def __init__(self) -> None:
        self.browser_manager: BrowserManager | None = None
        self.config: Config | None = None

    @classmethod
    async def init(cls) -> "WorkerContext":
        if cls._instance is None:
            cls._instance = cls()
            await cls._instance._setup()
        return cls._instance

    async def _setup(self):
        try:
            self.config = load()
            logger.info("Config successfully loaded")

            self.browser_manager = BrowserManager(self.config)
            await self.browser_manager.start()

            logger.success("WorkerContext successfully loaded")

        except Exception as exc:
            logger.exception(f"Error starting WorkerContext: {exc}")
            await self.cleanup()
            raise

    async def cleanup(self):
        logger.info("Exiting WorkerContext...")

        if self.browser_manager:
            await self.browser_manager.close()

        WorkerContext._instance = None


def get_worker_context():
    context = WorkerContext._instance
    if not context:
        logger.critical("Worker context is not initialized")
        raise RuntimeError("Worker context is not initialized")
    if not context.browser_manager:
        logger.critical("Worker browser is not initialized")
        raise RuntimeError("Worker browser is not initialized")
    if not context.config:
        logger.critical("Worker config is not initialized")
        raise RuntimeError("Worker config is not initialized")
    return context
