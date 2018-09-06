from celery.schedules import crontab

from app import app_instance
from app.celery import celery


@celery.task(name="app.celery_tasks.dispatch_task")
def dispatch_scheduled_item():
    # CELERYBEAT_SCHEDULE : <module name> : 
    app_instance.config['CELERYBEAT_SCHEDULE']['loading_task'] = {
        'task': 'report.utilities.data_loader',
        'schedule': crontab(
            **{app_instance.config['BEAT_PERIOD']: app_instance.config['BEAT_RATE']}
        )
    }
