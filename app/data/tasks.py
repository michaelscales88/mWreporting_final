from celery.schedules import crontab
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import func, and_
from sqlalchemy.dialects import postgresql

from app import celery, app
from app.database import data_session, local_session


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
    success = True
    from .models import CallTable
    try:
        results = data_session.query(CallTable).filter(
            and_(
                CallTable.start_time >= start_time,
                CallTable.end_time <= end_time,
            )
        )

        for r in results.all():
            exists = local_session.query(CallTable.call_id).filter_by(call_id=r.call_id).scalar() is not None
            if exists:
                print('record already exists')
            else:
                print('adding ', r.__dict__)
                local_session.add(CallTable(**r.__dict__))
        local_session.commit()
    except Exception as e:
        success = False
        print('Encountered an error', e)
        local_session.rollback()
        data_session.rollback()
    else:
        print('loaded data into local db')
    finally:
        local_session.remove()
        data_session.remove()

    return success


def get_test(start_time, end_time):
    from .models import CallTable
    try:
        new_results = local_session.query(CallTable).filter(
            and_(
                CallTable.start_time >= start_time,
                CallTable.end_time <= end_time,
            )
        )
    except Exception as e:
        print('Error getting records', e)
        local_session.rollback()
        return None
    else:
        print('from local database')
        return new_results
    finally:
        local_session.remove()


class SqlAlchemyTask(celery.Task):
    """An abstract Celery Task that ensures that the connection the the
    database is closed on task completion"""
    abstract = True

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        local_session.remove()
        data_session.remove()
        print('closed sessions.', local_session, data_session)


@celery.task(base=SqlAlchemyTask, max_retries=10, default_retry_delay=60)
def load_data(start_time=None, end_time=None, event_id=None):
    success = True
    from .models import CallTable
    try:
        results = data_session.query(CallTable).filter(
            and_(
                CallTable.start_time >= start_time,
                CallTable.end_time <= end_time,
            )
        )

        for r in results.all():
            exists = local_session.query(CallTable.call_id).filter_by(call_id=r.call_id).scalar() is not None
            if exists:
                print('record already exists')
            else:
                print('adding ', r.__dict__)
                local_session.add(CallTable(**r.__dict__))
        local_session.commit()
    except Exception as e:
        success = False
        print('Encountered an error', e)
        local_session.rollback()
        data_session.rollback()
    else:
        print('loaded data into local db')
    finally:
        local_session.remove()
        data_session.remove()

    return success


@celery.task(base=SqlAlchemyTask, max_retries=10, default_retry_delay=60)
def get_data(start_time=None, end_time=None, event_id=None):
    from .models import CallTable
    try:
        new_results = local_session.query(CallTable).filter(
            and_(
                CallTable.start_time >= start_time,
                CallTable.end_time <= end_time,
            )
        )
    except Exception as e:
        print('Error getting records', e)
        local_session.rollback()
        return None
    else:
        print('from local database')
        return new_results.frame()
    finally:
        local_session.remove()
