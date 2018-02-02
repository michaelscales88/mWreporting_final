# report/tasks.py
from flask import abort

from app.report.services import get_sla_report

# class SqlAlchemyTask(celery.Task):
#     """An abstract Celery Task that ensures that the connection the the
#     database is closed on task completion"""
#     abstract = True
#
#     def __call__(self, *args, **kwargs):
#         try:
#             return super().__call__(*args, **kwargs)
#         except DatabaseError:
#             app_meta_session.rollback()
#         finally:
#             app_meta_session.commit()
#         pass
#
#     def after_return(self, status, retval, task_id, args, kwargs, einfo):
#         app_meta_session.remove()
#         print(task_id, ' closed sessions: ', app_meta_session)
#         pass
#
#
# def add_scheduled_tasks(app):
#     # TODO automatically make yesterdays report at 12:01 AM
#     app.config['CELERYBEAT_SCHEDULE']['test'] = {
#         'task': 'app.data.tasks.load_data',
#         'schedule': crontab(minute='*/15'),
#         'args': ('date1', 'date2')
#     }
#     pass


def report_task(report_name, start_time=None, end_time=None, clients=None):
    if report_name == 'sla_report' and start_time and end_time:
        return get_sla_report(start_time, end_time, clients)
    else:
        return abort(404)
