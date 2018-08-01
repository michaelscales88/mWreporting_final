# report/services/sla_report.py
from datetime import timedelta

import numpy as np
import pandas as pd
from flask import current_app
from flask_mail import Message
from sqlalchemy.sql import and_

# celery = create_celery(create_application())
# from app.tasks import send_async_email
from app.utilities.helpers import query_to_frame, display_columns, get_model_by_tablename, export_excel


# from app.factories.application import create_application
# from app.factories.celery import create_celery


def get_td(interval, period):
    time_delta = {}
    if interval == 'D':
        time_delta['days'] = period
    elif interval == 'H':
        time_delta['hours'] = period
    elif interval == 'M':
        time_delta['minutes'] = period

    return timedelta(**time_delta)


def email_reports(start_time, end_time, interval='D', period=1):
    td = get_td(interval, period)
    filename = "test_report.xlsx"
    # output = io.BytesIO()
    # writer = pd.ExcelWriter(filename,
    #                         engine='xlsxwriter',
    #                         datetime_format='mmm d yyyy hh:mm:ss',
    #                         date_format='mmmm dd yyyy')
    while start_time <= end_time:
        report = get_sla_report(start_time, start_time + td)
        with report as report:
            print(report)
            msg = Message(
                "Report Test",
                recipients=[current_app.config['MAIL_USERNAME']],
                # attachments=Attachment(
                #     filename=filename,
                #     data=report.to_excel(writer)
                # )
            )
            msg.attach(filename, "xlsx", export_excel(report))
            # send_async_email(msg)
        # report.to_excel(writer)
        start_time += td

    return True


def run_reports(start_time, end_time, interval='D', period=1):
    td = get_td(interval, period)

    while start_time <= end_time:
        make_sla_report_model(start_time, start_time + td)
        start_time += td

    return True


def check_src_data_loaded(start_time, end_time, tables=("c_call", "c_event")):
    """
    Return True if the data is loaded for the date interval for all tables. Return False
    if not.
    :return:
    """
    table_loader = get_model_by_tablename("tables_loaded")
    for table_name in tables:
        if not table_loader.check_date_interval(start_time, end_time, table_name):
            print("Data not loaded:", start_time, end_time, table_name)
            return False
    return True


def make_summary(df):
    # Create row of sums
    sum_cols = [
        'I/C Presented',
        'I/C Live Answered',
        'I/C Abandoned',
        'Voice Mails',
        'Answered Incoming Duration',
        'Answered Wait Duration',
        'Lost Wait Duration',
        'Calls Ans Within 15',
        'Calls Ans Within 30',
        'Calls Ans Within 45',
        'Calls Ans Within 60',
        'Calls Ans Within 999',
        'Call Ans + 999'
    ]
    summary_frame = pd.DataFrame(
        [df[sum_cols].sum()], columns=sum_cols, index=['Summary']
    )
    summary_frame.insert(0, 'Client', ['Summary'])

    # Append column with max timedelta
    summary_frame['Longest Waiting Answered'] = pd.Series(
        df['Longest Waiting Answered'].max(), index=summary_frame.index
    )
    return df.append(summary_frame)


def compute_avgs(df):
    df['Incoming Live Answered (%)'] = np.where(
        df['I/C Live Answered'] < 1,
        df['I/C Live Answered'],
        df['I/C Live Answered'] / df['I/C Presented']
    )
    df['Incoming Received (%)'] = np.where(
        (df['I/C Live Answered'] + df['Voice Mails']) < 1,
        df['I/C Live Answered'],
        (df['I/C Live Answered'] + df['Voice Mails']) / df['I/C Presented']
    )
    df['Incoming Abandoned (%)'] = np.where(
        df['I/C Abandoned'] < 1,
        df['I/C Abandoned'],
        df['I/C Abandoned'] / df['I/C Presented']
    )
    df['Average Incoming Duration'] = np.where(
        df['I/C Live Answered'] < 1,
        df['Answered Incoming Duration'],
        df['Answered Incoming Duration'] / df['I/C Live Answered']
    )
    df['Average Wait Answered'] = np.where(
        df['I/C Live Answered'] < 1,
        df['Answered Wait Duration'],
        df['Answered Wait Duration'] / df['I/C Live Answered']
    )
    df['Average Wait Lost'] = np.where(
        (df['I/C Abandoned'] + df['Voice Mails']) < 1,
        df['Lost Wait Duration'],
        df['Lost Wait Duration'] / (df['I/C Abandoned'] + df['Voice Mails'])
    )
    df['PCA'] = np.where(
        df['I/C Presented'] < 1,
        df['I/C Presented'],
        (df['Calls Ans Within 15'] + df['Calls Ans Within 30']) / df['I/C Presented']
    )
    return df


def format_df(cell):
    if isinstance(cell, float):
        return "{:.0%}".format(cell)
    else:
        return cell


def empty_report():
    empty_model = get_report_model('sla_report')
    return query_to_frame(empty_model, is_report=True)


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


def report_exists_by_name(table_name, start_time, end_time):
    report_table = get_model_by_tablename(table_name)
    return hasattr(report_table, "exists") and report_table.exists(start_time, end_time)


def get_report_model(table_name, start_time=None, end_time=None):
    report_table = get_model_by_tablename(table_name)
    if start_time and end_time and hasattr(report_table, "get"):
        return report_table.get(start_time, end_time)
    else:
        return report_table.set_empty(report_table())


def get_calls_by_direction(table_name, start_time, end_time, call_direction=1):
    table = get_model_by_tablename(table_name)
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
    table = get_model_by_tablename(table_name)
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
