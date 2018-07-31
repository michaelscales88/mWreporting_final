# report/tasks.py
import datetime

from celery.schedules import crontab

from .builders import make_sla_report_model
from .utilities import (
    get_sla_report, empty_report, run_reports,
    email_reports, get_data, load_data_for_date_range,
    report_exists_by_name
)


def register_tasks(server):
    server.config['CELERYBEAT_SCHEDULE']['loading_task'] = {
        'task': 'app.data.services.loaders.data_loader',
        'schedule': crontab(
            **{server.config['BEAT_PERIOD']: server.config['BEAT_RATE']}
        ),
        'args': (server.config.get('DAYS_TO_LOAD', 5),)
    }
    end_time = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    start_time = end_time - datetime.timedelta(days=1)
    server.config['CELERYBEAT_SCHEDULE']['daily_report_task'] = {
        'task': 'app.report.services.sla_report.make_sla_report_model',
        'schedule': crontab(
            **{server.config['BEAT_PERIOD']: server.config['BEAT_RATE']}
        ),
        'args': (start_time, end_time,)
    }


def report_task(report_name, start_time=None, end_time=None, clients=None):
    if start_time and end_time:
        if report_name == 'sla_report':
            return get_sla_report(start_time, end_time, clients)
        elif report_name == 'run_series':
            run_reports(start_time, end_time, interval='H', period=12)
            return True
        elif report_name == 'email_series':
            email_reports(start_time, end_time, interval='H', period=12)
            return True
    else:
        return empty_report()


def data_task(task_name, start_time=None, end_time=None, table=None):
    # Valid table
    if start_time and end_time:
        if task_name == 'LOAD':
            # loading tables
            for table in ('c_call', 'c_event'):
                if load_data_for_date_range(table, start_time, end_time):
                    print("Loaded data for", table, start_time, end_time)
                else:
                    print("Error loading data for", table, start_time, end_time)
            # Load data for selected tables - Celery
            # load_job = group(
            #     [load_data_for_date_range.s(table, start_time, end_time) for table in tables]
            # )
            # result = load_job.apply_async()
            # result.join()
            # print("passed loading")
            # # TODO: get more information from this
            # for status in cr.GroupResult(results=result):
            #     print(status)
            return True
        elif isinstance(table, str):
            # a table is provided
            return get_data(table, start_time, end_time)
        else:
            return False
    else:
        # Empty table
        print("else returning data")
        if isinstance(table, str):
            return get_data(table, datetime.now(), datetime.now())
        else:
            return False


def get_sla_report(start_time, end_time, clients=None):
    # Check the report model exists
    report_exists = report_exists_by_name('sla_report', start_time, end_time)
    print("get_sla_report")
    try:
        # If the report does not exist make a report.
        # Raise AssertionError if a report is not made.
        if not report_exists:
            report_made = make_sla_report_model(start_time, end_time)
            print("made report:", report_made)
            if not report_made:
                raise AssertionError("Report not made.")

        report_query = get_report_model('sla_report', start_time, end_time)

        if not report_query:
            raise AssertionError("Report not found.")

        report_frame = query_to_frame(report_query, is_report=True)

        # Filter the report to only include desired clients
        if clients:
            report_frame = report_frame.filter(items=clients, axis=0)

        # Make the visible index the DID extension + client name,
        # or just DID extension if no name exists
        report_frame = add_frame_alias("client", report_frame)

        if not report_frame.empty:
            # Create programmatic columns and rows
            report_frame = make_summary(report_frame)
            report_frame = compute_avgs(report_frame)

            # Filter out columns containing raw data
            columns = display_columns('sla_report')
            report_frame = report_frame[columns]

    except AssertionError as e:
        if e == "Report not made.":
            print("Error: report not made")
        if e == "Report not found.":
            print("Error: report not found.")

        return empty_report()
    else:
        # Prettify percentages
        return report_frame.applymap(format_df)