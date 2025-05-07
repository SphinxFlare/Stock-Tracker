# celery_worker.py

from celery import Celery
from App.celery_config import (
    CELERY_BROKER_URL,
    CELERY_RESULT_BACKEND,
    CELERY_TIMEZONE,
    CELERYBEAT_SCHEDULE,
)

celery = Celery('stock_tasks')

celery.config_from_object({
    'broker_url': CELERY_BROKER_URL,
    'result_backend': CELERY_RESULT_BACKEND,
    'timezone': CELERY_TIMEZONE,
    'enable_utc': True,
})

celery.conf.beat_schedule = CELERYBEAT_SCHEDULE
# celery.autodiscover_tasks(['App.tasks.update_snapshots'])