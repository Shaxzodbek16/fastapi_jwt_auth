from celery import Celery

from app.core.settings import get_settings, Settings

settings: Settings = get_settings()

app = Celery(
    "worker",
    broker=settings.GET_REDIS_URL,
    backend=settings.GET_REDIS_URL,
)

app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    worker_max_tasks_per_child=100,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    result_expires=3600 * 12,  # 12 hours
    broker_connection_retry_on_startup=True,
    task_default_queue="default",
    timezone="Asia/Tashkent",
)

app.autodiscover_tasks(["app.api.tasks"])
