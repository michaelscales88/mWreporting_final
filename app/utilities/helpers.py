# services/tasks.py
import io
import pandas as pd
from datetime import datetime
from dateutil.parser import parse
from flask import jsonify, current_app, request
from json import loads
from flask_sqlalchemy import Model, BaseQuery
from sqlalchemy.inspection import inspect
from functools import wraps
from .base_model import BaseModel


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


# Other Tasks
def return_task(fn):

    @wraps(fn)
    def wrapper(*args, **kwargs):
        result = None
        try:
            result = fn(*args, **kwargs)
            print(type(result), result)
            if isinstance(result, bool):
                # Boolean result for model updates
                key_words = {}
            elif isinstance(result, (tuple, list)):
                key_words = {
                    "data": result
                }
            elif isinstance(result, BaseQuery):
                key_words = {
                    "data": []
                }
            elif isinstance(result, dict) and isinstance(result.get("data"), list):
                key_words = result
            else:
                key_words = {
                    "data": result.to_dict(orient='split')['data']
                }
        except AttributeError:
            # Exclude Response objects
            return result
        except Exception as e:
            if current_app.config.get('NOISY_ERROR'):
                import sys
                import traceback
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback.print_exception(exc_type, exc_value, exc_traceback,
                                          limit=2, file=sys.stdout)
            return jsonify(
                status=404,
                error=str(e),
                data=[]
            )
        else:
            print(key_words)
            return jsonify(
                **key_words
            )

    return wrapper


def to_datetime(value, name, *args):
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


def get_model(tablename):
    for c in BaseModel._decl_class_registry.values():
        if hasattr(c, '__tablename__') and c.__tablename__ == tablename:
            return c


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
    if isinstance(query_obj, Model):
        return getattr(query_obj, column_name, None)
    if isinstance(query_obj, dict):
        return query_obj.get(column_name)


def parse_time(s):
    try:
        ret = parse(s)
    except ValueError:
        ret = datetime.utcfromtimestamp(s)
    return ret


def export_excel(df):
    with io.BytesIO() as buffer:
        writer = pd.ExcelWriter(buffer)
        df.to_excel(writer)
        writer.save()
        return buffer.getvalue()
