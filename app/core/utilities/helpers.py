# services/tasks.py
import io
import pandas as pd
from dateutil.parser import parse
from json import loads
from flask_sqlalchemy import Model
from sqlalchemy.inspection import inspect
from app.extensions.base_model import BaseModel


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


def get_model_by_tablename(tablename):
    for c in BaseModel._decl_class_registry.values():
        if hasattr(c, '__tablename__') and c.__tablename__ == tablename:
            return c


def get_model_headers(model_name=None):
    model = get_model_by_tablename(model_name)
    return list(model.headers) if model else None


def get_pk(table):
    return inspect(table).primary_key[0].name


def get_foreign_id(query_obj, column_name):
    if isinstance(query_obj, Model):
        return getattr(query_obj, column_name, None)
    if isinstance(query_obj, dict):
        return query_obj.get(column_name)


def export_excel(df):
    with io.BytesIO() as buffer:
        writer = pd.ExcelWriter(buffer)
        df.to_excel(writer)
        writer.save()
        return buffer.getvalue()


def save_xls(list_dfs, xls_path):
    writer = pd.ExcelWriter(xls_path)
    for n, df in enumerate(list_dfs):
        df.to_excel(writer, '{sheet_name}'.format(sheet_name=df.name))
    writer.save()
