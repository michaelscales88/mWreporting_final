# services/tasks.py
import os
import pandas as pd
from flask import jsonify, current_app
from dateutil.parser import parse
from json import loads
from sqlalchemy.inspection import inspect
from functools import wraps


# Other Tasks
def return_task(fn):

    @wraps(fn)
    def wrapper(*args, **kwds):
        try:
            frame = fn(*args, **kwds)
            if isinstance(frame, bool):
                # Boolean frame for model updates
                key_words = {}
            else:
                data = frame.to_dict(orient='split')
                key_words = {
                    "data": data['data']
                }
        except Exception as e:
            if current_app.config.get('NOISY_ERROR'):
                import sys
                import traceback
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback.print_exception(exc_type, exc_value, exc_traceback,
                                          limit=2, file=sys.stdout)
            return jsonify(
                status=404,
                error=str(e)
            )
        else:
            return jsonify(
                **key_words
            )

    return wrapper


def to_datetime(value, name):
    try:
        dt = parse(value)
    except (ValueError, OverflowError):
        raise ValueError(
            "{param} is an invalid time value."
            "You gave the value: {val}".format(param=name, val=value)
        )
    return dt


def to_list(value):
    return loads(value)


def to_bool(value):
    return loads(value) is True


def get_model(model=None):
    from app.client.models import _mmap as client_map
    from app.data.models import _mmap as model_map
    from app.report.models import _mmap as report_map

    # Access models from any module by name
    all_map = {
        **client_map,
        **model_map,
        **report_map
    }

    return all_map.get(model, None)


def get_model_headers(model_name=None):
    model = get_model(model_name)
    return list(model.headers) if model else None


def display_columns(model_name=None):
    headers = get_model_headers(model_name)
    if headers:
        if model_name == 'sla_report':
            return ['Client'] + headers
        else:
            return headers
    else:
        return []


def query_to_frame(query, is_report=False):
    if is_report:
        # Convert JSON report to DataFrame
        return pd.DataFrame.from_dict(query.data, orient='index')
    else:
        # Convert ORM model to DataFrame
        q_entity = query.column_descriptions[0]['type']
        frame = pd.read_sql(query.statement, query.session.bind)
        return frame[get_model_headers(q_entity.__tablename__)]


def get_pk(table):
    return inspect(table).primary_key[0].name


def get_foreign_id(query_obj, column_name):
    return getattr(query_obj, column_name, None)


def make_dir(directory):
    os.makedirs(directory, exist_ok=True)
