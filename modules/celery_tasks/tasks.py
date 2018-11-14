from flask import current_app
from celery.schedules import crontab

from modules.celery import celery


@celery.task(name="app.celery_tasks.dispatch_task")
def dispatch_scheduled_item():
    # CELERYBEAT_SCHEDULE : <module name> : 
    current_app.config['CELERYBEAT_SCHEDULE']['loading_task'] = {
        'task': 'report.utilities.data_loader',
        'schedule': crontab(
            **{current_app.config['BEAT_PERIOD']: current_app.config['BEAT_RATE']}
        )
    }
