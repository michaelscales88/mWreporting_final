# data/tasks.py
from flask import abort


from .services import get_data, load_data_for_date_range

# class SqlAlchemyTask(celery.Task):
#     """An abstract Celery Task that ensures that the connection the the
#     database is closed on task completion"""
#     abstract = True
#
#     def __call__(self, *args, **kwargs):
#         try:
#             return super().__call__(*args, **kwargs)
#         except DatabaseError:
#             loc_data_session.rollback()
#         finally:
#             loc_data_session.commit()
#         pass
#
#     def after_return(self, status, retval, task_id, args, kwargs, einfo):
#         loc_data_session.remove()
#         ext_data_session.remove()
#         print(task_id, ' closed sessions: ', loc_data_session, ext_data_session)
#         pass
#
#
# def add_scheduled_tasks(app):
#     app.config['CELERYBEAT_SCHEDULE']['test'] = {
#         'task': 'app.data.tasks.load_data',
#         'schedule': crontab(minute='*/15'),
#         'args': ('date1', 'date2')
#     }
#     pass

# @celery.task(base=SqlAlchemyTask, max_retries=10, default_retry_delay=60)
# def get_data(start_time=None, end_time=None, event_id=None):
#     return CallTableModel.query.filter(
#         and_(
#             CallTableModel.start_time >= start_time,
#             CallTableModel.end_time <= end_time,
#         )
#     )


def data_task(task_name, start_time=None, end_time=None):
    if start_time and end_time:
        result = None
        if task_name == 'get':
            result = get_data('c_call', start_time, end_time)
        elif task_name == 'load':
            print('loading data')
            result1 = load_data_for_date_range('c_call', start_time, end_time)
            result2 = load_data_for_date_range('c_event', start_time, end_time)
            # result2 = True
            result = result1 and result2
        return result
    else:
        return abort(404)
