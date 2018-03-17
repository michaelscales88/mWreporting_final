# report/tasks.py
from backend.report.services import get_sla_report, empty_report

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
#     app.config['CELERYBEAT_SCHEDULE']['tests'] = {
#         'task': 'app.data.tasks.load_data',
#         'schedule': crontab(minute='*/15'),
#         'args': ('date1', 'date2')
#     }
#     pass


def report_task(report_name, start_time=None, end_time=None, clients=None):
    print("hit report_task")
    if report_name == 'sla_report':
        if start_time and end_time:
            report = get_sla_report(start_time, end_time, clients)
            return report
        else:
            return empty_report()
    else:
        return empty_report()
