# report/tasks.py
import datetime
import pandas as pd
from celery.schedules import crontab

from .utilities import (
    report_loader, empty_report, run_reports,
    email_reports, get_data, load_data_for_date_range,
    report_exists_by_name, make_sla_report_model,
    get_report_model, add_frame_alias, compute_avgs,
    format_df, make_summary
)
from app.utilities import query_to_frame, display_columns


def register_tasks(server_instance):
    server_instance.config['CELERYBEAT_SCHEDULE']['loading_task'] = {
        'task': 'report.utilities.data_loader',
        'schedule': crontab(
            **{server_instance.config['BEAT_PERIOD']: server_instance.config['BEAT_RATE']}
        )
    }
    server_instance.config['CELERYBEAT_SCHEDULE']['report_task'] = {
        'task': 'report.utilities.report_loader',
        'schedule': crontab(
            **{server_instance.config['BEAT_PERIOD']: server_instance.config['BEAT_RATE']}
        )
    }


def report_task(report_name, start_time=None, end_time=None, clients=None):
    if start_time and end_time:
        if report_name == 'sla_report':
            return report_loader(start_time, end_time, clients)
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


def get_sla_report(start_time, end_time, clients=()):
    # Check the report model exists
    report_exists = report_exists_by_name('sla_report', start_time, end_time)

    # If the report does not exist make a report.
    if report_exists:
        print("report exists")
        report_query = get_report_model('sla_report', start_time, end_time)

        if not report_query:
            raise AssertionError("Report not found.")
    else:
        print("trying to make report")
        report_made = make_sla_report_model(start_time=start_time, end_time=end_time)
        if not report_made:
            print("report is not Made")
            raise AssertionError("Report not made.")

        report_query = get_report_model('sla_report', start_time, end_time)

    df = query_to_frame(report_query, is_report=True)

    # Filter the report to only include desired clients
    if clients and len(clients) > 0:
        df = df.filter(items=clients, axis=0)

    # Make the visible index the DID extension + client name,
    # or just DID extension if no name exists
    df = add_frame_alias("client_model", df)

    if not df.empty:
        # Create programmatic columns and rows
        df = make_summary(df)
        df = compute_avgs(df)

        # Filter out columns containing raw data
        columns = display_columns('sla_report')
        df = df[columns]
        print("not empty settings")

    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    #     print(df)
    # Prettify percentages
    return df.applymap(format_df)
