import pandas as pd
from flask import jsonify
from dateutil.parser import parse
from kombu import serialization
from sqlalchemy.inspection import inspect
from functools import wraps


from app import celery, mail


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
                    # "recordsTotal": len(frame.index),
                    # "recordsFiltered": len(frame.index),
                    "data": data['data']
                }
        except Exception as e:
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


def get_model_headers(model=None):
    from app.client.tasks import _mmap as client_map
    from app.data.tasks import _mmap as model_map
    from app.report.tasks import _mmap as report_map

    all_map = {
        **client_map,
        **model_map,
        **report_map
    }
    if model in all_map.keys():
        return all_map.get(model, None).__repr_attrs__
    return None


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


@celery.task
def send_async_email(msg):
    """Background task to send an email with Flask-Mail."""
    mail.send(msg)


def serialization_register_json():
    """Register a encoder/decoder for JSON serialization."""

    from anyjson import loads as json_loads, dumps as json_dumps

    def _loads(obj):
        if isinstance(obj, serialization.bytes_t):
            obj = obj.decode()
        # Make this the custom loader
        obj = json_loads(obj)
        if hasattr(obj, 'get') and obj.get('traceback') is not None:
            try:
                exc_type = obj['result']['exc_type']
                exc_message = obj['result']['exc_message']
            except KeyError:
                pass
            else:
                exc_type = getattr(obj, exc_type)
                obj['result'] = exc_type(exc_message)
        return obj

    serialization.registry.register('json', json_dumps, _loads,
                                    content_type='application/json',
                                    content_encoding='utf-8')
