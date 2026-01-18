from typing import Annotated

from celery import Celery
from fastapi import Depends

from app.celery_app.celery_app import celery_app


def get_celery_app() -> Celery:
    """Get celery app dependency"""
    return celery_app


CeleryDep = Annotated[Celery, Depends(get_celery_app)]
