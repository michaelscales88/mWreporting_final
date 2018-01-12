# util/tasks.py
import pandas as pd
from flask import jsonify, current_app
from dateutil.parser import parse
from sqlalchemy.inspection import inspect
from functools import wraps


from app import celery, mail


# Celery Tasks
@celery.task
def send_async_email(msg):
    """Background task to send an email with Flask-Mail."""
    mail.send(msg)


# Other Tasks
def return_task(fn):

    @wraps(fn)
    def wrapper(*args, **kwds):
        try:
            frame, status = fn(*args, **kwds)
            if isinstance(frame, bool):
                # Boolean frame for model updates
                key_words = {}
            else:
                # Transform data for AJAX
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
                status=status,
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


def get_model(model=None):
    from app.client.tasks import _mmap as client_map
    from app.data.tasks import _mmap as model_map
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


def query_to_frame(query, is_report=False):
    if is_report:
        # convert the json_type from report into a frame
        # frame =
        frame = None
        pass
    else:
        q_entity = query.column_descriptions[0]['type']
        frame = pd.read_sql(query.statement, query.session.bind)
        frame = frame[get_model_headers(q_entity.__tablename__)]
    return frame


def get_pk(table):
    return inspect(table).primary_key[0].name


def get_foreign_id(query_obj, column_name):
    return getattr(query_obj, column_name, None)


# def serialization_register_json():
#     """Register a encoder/decoder for JSON serialization."""

    # from anyjson import loads as json_loads, dumps as json_dumps
    #
    # def _loads(obj):
    #     if isinstance(obj, serialization.bytes_t):
    #         obj = obj.decode()
    #     # Make this the custom loader
    #     obj = json_loads(obj)
    #     if hasattr(obj, 'get') and obj.get('traceback') is not None:
    #         try:
    #             exc_type = obj['result']['exc_type']
    #             exc_message = obj['result']['exc_message']
    #         except KeyError:
    #             pass
    #         else:
    #             exc_type = getattr(obj, exc_type)
    #             obj['result'] = exc_type(exc_message)
    #     return obj

    # serialization.registry.register(
    #     'json', my_dumps, my_loads,
    #     content_type='application/json'
    # )
