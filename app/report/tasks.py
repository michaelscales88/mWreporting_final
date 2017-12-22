from sqlalchemy.exc import DatabaseError
from sqlalchemy.sql import and_
from sqlalchemy.orm.exc import NoResultFound

from app import celery

from .models import SLAReport, app_meta_session


_mmap = {
    "sla_report": SLAReport
}


def get_report_headers(model=None):
    if model in _mmap.keys():
        return _mmap.get(model, None).__repr_attrs__
    return None


def test_report(start_date, end_date, report_id=None):
    """
    Get report from id if it exists or make the report for the interval
    """
    # Add report model stuff here
    print('for sure i did this')
    return [{
        'id': 'Test Successful',
        'date': start_date,
        'report': end_date,
        'notes': report_id
    }], None, 200


def test_or_make_report(start_time, end_time, report_id=None):
    """
    Get report from id if it exists or make the report for the interval
    """
    report = None
    try:
        if report_id:
            report = SLAReport.query.get_or(report_id)
        else:
            report = SLAReport.query.filter(
                and_(
                    SLAReport.start_time == start_time,
                    SLAReport.end_time == end_time,
                )
            )

        if report:

            print(report)
            report = "Success"

    except (DatabaseError, NoResultFound):
        app_meta_session.rollback()
    else:
        app_meta_session.commit()
    finally:
        app_meta_session.remove()
    # Add report model stuff here
    print('for sure i did this')
    return [{
        'id': 'Test Successful',
        'date': start_time,
        'report': end_time,
        'notes': report
    }], None, 200


class SqlAlchemyTask(celery.Task):
    """An abstract Celery Task that ensures that the connection the the
    database is closed on task completion"""
    abstract = True

    def __call__(self, *args, **kwargs):
        try:
            return super().__call__(*args, **kwargs)
        except DatabaseError:
            app_meta_session.rollback()
        finally:
            app_meta_session.commit()

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        app_meta_session.remove()
        print(task_id, ' closed sessions: ', app_meta_session)


@celery.task(base=SqlAlchemyTask, max_retries=10, default_retry_delay=60)
def fetch_or_make_report(start_time, end_time):
    """
    Get report from id if it exists or make the report for the interval
    """
    from datetime import timedelta
    report_id = SLAReport.query.filter(
        and_(
            SLAReport.start_time == start_time,
            SLAReport.end_time == end_time,
        )
    )
    report = SLAReport.query.get_or(report_id)
    if report:
        pass
    # Add report model stuff here
    print('for sure i did this')
    return [{
        'id': 'Test Successful',
        'date': start_time,
        'report': end_time,
        'notes': report
    }]
