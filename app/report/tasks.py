from sqlalchemy.orm.exc import NoResultFound
from celery.schedules import crontab

from app import celery


def add_scheduled_tasks(app):
    app.config['CELERYBEAT_SCHEDULE']['test'] = {
        'task': 'app.report.tasks.load_data',
        'schedule': crontab(minute='*/1'),
        'args': ('date1', 'date2')
    }


class SqlAlchemyTask(celery.Task):
    """An abstract Celery Task that ensures that the connection the the
    database is closed on task completion"""
    abstract = True

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        print('closing connection')


@celery.task
def fetch_report(start_date, end_date, report_id=None):
    """
    Get report from id if it exists or make the report for the interval
    """
    # Add report model stuff here
    print('for sure i did this')
    return [{
        'test': 'Test Successful',
        'start_date': start_date,
        'end_date': end_date,
        'report_id': report_id
    }]


@celery.task(base=SqlAlchemyTask, max_retries=10, default_retry_delay=60)
def load_data(start_date, end_date, event_id=None):
    # event_id can be call_id or event_id from models.py
    try:
        print(start_date, end_date, event_id)
    except NoResultFound as exc:
        raise load_data.retry(exc=exc)
    # do something with the user
    print('loading data')
