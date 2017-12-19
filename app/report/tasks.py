from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import func, and_
from sqlalchemy.dialects import postgresql
from celery.schedules import crontab
from datetime import datetime

from app import celery
from app.database import pg_session


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
        pg_session.remove()
        print('closed session.', pg_session)


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
    from .models import CallTable, EventTable
    from sqlalchemy import cast, DATE
    start_date = end_date = datetime.today().date()
    try:
        print(start_date, end_date, event_id)
        results = pg_session.query(CallTable).filter(cast(CallTable.start_time, DATE) == start_date)
        print(results)
        print(str(results.statement.compile(dialect=postgresql.dialect())))
    except NoResultFound as exc:
        print('No Result Found')
        raise load_data.retry(exc=exc)
    # do something with the user
    print('loading data')
    for r in results.all():
        print(r)
