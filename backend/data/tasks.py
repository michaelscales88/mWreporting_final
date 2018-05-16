# data/tasks.py
from celery.schedules import crontab

from .services import get_data, load_data_for_date_range, empty_data


def register_tasks(server):
    server.config['CELERYBEAT_SCHEDULE']['loading_task'] = {
        'task': 'backend.data.services.loaders.data_loader',
        'schedule': crontab(
            **{server.config['BEAT_PERIOD']: server.config['BEAT_RATE']}
        ),
        'args': (server.config.get('DAYS_TO_LOAD', 5),)
    }


def data_task(task_name, start_time=None, end_time=None, tables=('c_call', 'c_event')):
    if start_time and end_time and isinstance(tables, (list, tuple)):
        if task_name == 'LOAD':
            print("trying to load")
            [load_data_for_date_range(table, start_time, end_time) for table in tables]
            # Load data for selected tables - Celery
            # load_job = group(
            #     [load_data_for_date_range.s(table, start_time, end_time) for table in tables]
            # )
            # result = load_job.apply_async()
            # result.join()
            # print("passed loading")
            # # TODO: get more information from this
            # for status in cr.GroupResult(results=result):
            #     print(status)
            return True
        elif task_name == 'GET':
            print("start get", tables)
            return get_data(tables[0], start_time, end_time)
        else:
            return empty_data(tables[0])
    else:
        return empty_data(tables[0] if isinstance(tables, (list, tuple)) else tables)
