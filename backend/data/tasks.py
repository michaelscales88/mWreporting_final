# data/tasks.py
from flask import abort
from celery import group, result as cr

from .services import get_data, load_data_for_date_range


def data_task(task_name, start_time=None, end_time=None, tables=('c_call', 'c_event')):
    if start_time and end_time:
        result = None
        if task_name == 'GET':
            result = get_data(tables[0], start_time, end_time)
        elif task_name == 'LOAD':
            print("trying to load")
            # Load data for selected tables
            load_job = group(
                [load_data_for_date_range.s(table, start_time, end_time) for table in tables]
            )
            result = load_job.apply_async()
            result.join()
            print("passed loading")
            # TODO: get more information from this
            for status in cr.GroupResult(results=result):
                print(status)
            return True
        return result
    else:
        return abort(404)
