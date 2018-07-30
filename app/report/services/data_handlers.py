# data/services/data.py
from sqlalchemy.sql import and_

from app.services.app_tasks import get_model, query_to_frame


def get_data_for_table(table_name, start_time, end_time):
    table = get_model(table_name)
    return table.query.filter(
        and_(
            table.start_time >= start_time,
            table.end_time <= end_time
        )
    )


def get_data(table_name, start_time, end_time):
    return query_to_frame(get_data_for_table(table_name, start_time, end_time))
