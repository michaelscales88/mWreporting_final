# data/services/data.py
from sqlalchemy.sql import and_

from backend.services.app_tasks import get_model
from .loaders import empty_data


def get_data_for_table(table_name, start_time, end_time):
    table = get_model(table_name)
    return table.query.filter(
        and_(
            table.start_time >= start_time,
            table.end_time <= end_time
        )
    )


def get_data(table_name, start_time, end_time):
    print("start get data")
    data_query = get_data_for_table(table_name, start_time, end_time)
    # print("got query", data_query)
    # if data_query.first() is None:
    #     print("found none")
    #     data_query = empty_data(table_name)
    # print("found data", data_query.all())
    return data_query
