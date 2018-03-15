# data/tasks.py
import logging
from celery.schedules import crontab
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
def add_scheduled_tasks(app):
    # logging.info("Updating scheduled tasks:")
    app.config['CELERYBEAT_SCHEDULE']['test'] = {
        'task': 'backend.data.services.loaders.data_loader',
        'schedule': crontab(minute='*/1'),
        'args': (100,)
    }
    # logging.info(app.config['CELERYBEAT_SCHEDULE']['test'])
    print("ran schedule tasks")


def data_task(task_name, start_time=None, end_time=None):
    if start_time and end_time:
        result = None
        if task_name == 'get':
            result = get_data('c_call', start_time, end_time)
        elif task_name == 'load':
            print('loading data')
            result1 = load_data_for_date_range('c_call', start_time, end_time)
            result2 = load_data_for_date_range('c_event', start_time, end_time)

            # result1 = load_data_for_date_range.delay('c_call', start_time, end_time)
            # result1 = test_load_data_for_date_range.delay('c_call', start_time, end_time)
            # print('about to wait')
            # result1.wait()
            # print('done waiting')
            # result2 = True
            result = result1 and result2
        return result
    else:
        return abort(404)
