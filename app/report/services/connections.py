# report/services/connections.py
from app.services.app_tasks import get_model
from sqlalchemy.sql import and_


def report_exists_by_name(table_name, start_time, end_time):
    return False if get_report_model(table_name, start_time, end_time) is None else True


def get_report_model(table_name, start_time, end_time):
    table = get_model(table_name)
    return table.query.filter(
        and_(
            table.start_time == start_time,
            table.end_time == end_time,
        )
    ).first()


def get_calls_by_direction(table_name, start_time, end_time, call_direction=1):
    table = get_model(table_name)
    return table.query.filter(
        and_(
            table.start_time >= start_time,
            table.end_time <= end_time,
            table.call_direction == call_direction
        )
    )


def add_frame_alias(table_name, frame):
    # Show the clients as row names
    table = get_model(table_name)
    aliases = None
    if not frame.empty and hasattr(table, "client_name"):
        aliases = table.query.filter(table.client_name.in_(list(frame.index))).all()
        print(aliases)
    frame.insert(0, "Client", aliases if aliases else list(frame.index))
    return frame
