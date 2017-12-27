from celery.schedules import crontab

from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import func, and_
from sqlalchemy.dialects import postgresql

from .models import CallTable, EventTable
from app import app, celery
from app.database import get_session


ext_session = get_session(app.config['EXTERNAL_DATABASE_URI'], readonly=True)
local_session = get_session(app.config['SQLALCHEMY_DATABASE_URI'])
CallTable.set_session(local_session)
EventTable.set_session(local_session)


_mmap = {
    'c_call': CallTable,
    'c_event': EventTable
}


def get_records():
    return CallTable.query


def add_scheduled_tasks(app):
    # app.config['CELERYBEAT_SCHEDULE']['test'] = {
    #     'task': 'app.data.tasks.load_data',
    #     'schedule': crontab(minute='*/15'),
    #     'args': ('date1', 'date2')
    # }
    pass


def data_task(task, start_time, end_time, id=None):
    if task == 'load_test':
        result = load_test(start_time, end_time)
        status = 'Test'
        tb = 'Okay'
    elif task == 'get_test':
        result = get_test(start_time, end_time)
        status = 'Test'
        tb = 'Okay'
    else:
        if task == 'load':
            async_result = load_data.delay(start_time, end_time)
        else:
            async_result = get_data.delay(start_time, end_time)
        try:
            result = async_result.get(timeout=5, propagate=False)
        except TimeoutError:
            result = None
        status = async_result.status
        tb = async_result.traceback
    return result, status, tb


def load_test(start_time, end_time):
    pass
    # try:
    #     results = CallTable.query.filter(
    #         and_(
    #             CallTable.start_time >= start_time,
    #             CallTable.end_time <= end_time,
    #         )
    #     )
    #
    #     for r in results.all():
    #         exists = LocalCallTable.query.get_or(r.call_id) is not None
    #         if exists:
    #             print('record already exists')
    #         else:
    #             print('adding ', r.__dict__)
    #             LocalCallTable(**r.__dict__).save()
    # except (DatabaseError, NoResultFound):
    #     loc_data_session.rollback()
    #     ext_data_session.rollback()
    # else:
    #     loc_data_session.commit()
    # finally:
    #     loc_data_session.remove()
    #     ext_data_session.remove()
    # return True


def get_test(start_time, end_time):
    return LocalCallTable.query.filter(
        and_(
            LocalCallTable.start_time >= start_time,
            LocalCallTable.end_time <= end_time,
        )
    )


class SqlAlchemyTask(celery.Task):
    """An abstract Celery Task that ensures that the connection the the
    database is closed on task completion"""
    abstract = True

    def __call__(self, *args, **kwargs):
        # try:
        #     return super().__call__(*args, **kwargs)
        # except DatabaseError:
        #     loc_data_session.rollback()
        # finally:
        #     loc_data_session.commit()
        pass

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        # loc_data_session.remove()
        # ext_data_session.remove()
        # print(task_id, ' closed sessions: ', loc_data_session, ext_data_session)
        pass


@celery.task(base=SqlAlchemyTask, max_retries=10, default_retry_delay=60)
def load_data(start_time=None, end_time=None, event_id=None):
    success = True
    results = CallTable.query.filter(
        and_(
            CallTable.start_time >= start_time,
            CallTable.end_time <= end_time,
        )
    )
    print(results)
    print(str(results.statement.compile(dialect=postgresql.dialect())))

    for r in results.all():
        exists = LocalCallTable.query.get_or(r.call_id) is not None
        if exists:
            print('record already exists')
        else:
            print('adding ', r.__dict__)
            LocalCallTable(**r.__dict__).save()

    return success


@celery.task(base=SqlAlchemyTask, max_retries=10, default_retry_delay=60)
def get_data(start_time=None, end_time=None, event_id=None):
    return CallTable.query.filter(
        and_(
            CallTable.start_time >= start_time,
            CallTable.end_time <= end_time,
        )
    )
