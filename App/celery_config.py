# celery_config.py

from celery.schedules import crontab

# Configure Celery to use Redis as the message broker
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_ENABLE_UTC = True


CELERYBEAT_SCHEDULE = {
    # 'update_snapshots_every_2h': {
    #     'task': 'App.tasks.update_snapshots.update_all_users_snapshots',
    #     'schedule': crontab(minute=0, hour='12'),
    #     'args': (),
    # },
}