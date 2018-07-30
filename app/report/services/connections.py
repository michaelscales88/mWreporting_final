# report/services/connections.py
from app.services.app_tasks import get_model
from sqlalchemy.sql import and_


def report_exists_by_name(table_name, start_time, end_time):
    report_table = get_model(table_name)
    return hasattr(report_table, "exists") and report_table.exists(start_time, end_time)


def get_report_model(table_name, start_time=None, end_time=None):
    report_table = get_model(table_name)
    if start_time and end_time and hasattr(report_table, "get"):
        return report_table.get(start_time, end_time)
    else:
        return report_table.set_empty(report_table())


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
    print("running frame alias")
    # Show the clients as row names
    table = get_model(table_name)
    aliases = []
    print(table)
    if not frame.empty and hasattr(table, "client_name"):
        print(table.all())
        # aliases = table.query.filter(table.client_name.in_(list(frame.index))).all()
        print('found aliases', aliases)
        for index in list(frame.index):
            print('frame index')
            client = table.get(index)
            print(client)
            if client:
                # aliases.append("{name} ({ext})".format(name=client.client_name, ext=client.ext))
                aliases.append("{name}".format(name=client.client_name))
            else:
                aliases.append(index)
        print('aliases:', aliases)
    frame.insert(0, "Client", aliases if aliases else list(frame.index))
    return frame
