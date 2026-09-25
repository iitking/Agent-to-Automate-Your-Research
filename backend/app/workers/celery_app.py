from app.core.config import settings
from app.core.logging import logger

try:
    from celery import Celery
    celery_app = Celery(
        "research_worker",
        broker=settings.REDIS_URL,
        backend=settings.REDIS_URL,
    )
    celery_app.conf.update(
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"],
        timezone="UTC",
        enable_utc=True,
    )
except ImportError:
    celery_app = None
    logger.info("Celery is not installed or optional; using FastAPI native background tasks.")
