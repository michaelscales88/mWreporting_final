# data/tasks.py
from datetime import datetime
from celery.schedules import crontab

from .services import get_data, load_data_for_date_range


def register_tasks(server):
    server.config['CELERYBEAT_SCHEDULE']['loading_task'] = {
        'task': 'backend.data.services.loaders.data_loader',
        'schedule': crontab(
            **{server.config['BEAT_PERIOD']: server.config['BEAT_RATE']}
        ),
        'args': (server.config.get('DAYS_TO_LOAD', 5),)
    }


def data_task(task_name, start_time=None, end_time=None, table=None):
    # Valid table
    if start_time and end_time:
        if task_name == 'LOAD':
            # loading tables
            for table in ('c_call', 'c_event'):
                if load_data_for_date_range(table, start_time, end_time):
                    print("Loaded data for", table, start_time, end_time)
                else:
                    print("Error loading data for", table, start_time, end_time)
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
        elif isinstance(table, str):
            # a table is provided
            return get_data(table, start_time, end_time)
        else:
            return False
    else:
        # Empty table
        print("else returning data")
        if isinstance(table, str):
            return get_data(table, datetime.now(), datetime.now())
        else:
            return False
