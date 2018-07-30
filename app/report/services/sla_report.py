# report/services/sla_report.py
import pandas as pd
import numpy as np
import io
from collections import OrderedDict
from datetime import timedelta, datetime
from flask import current_app
from flask_mail import Message, Attachment
from sqlalchemy.exc import DatabaseError


from .connections import get_report_model, report_exists_by_name, get_calls_by_direction, add_frame_alias
from app.tasks import send_async_email
from app.services.app_tasks import query_to_frame, display_columns, get_model, export_excel
from app.report.models import SlaReportModel
from app.factories.application import create_application
from app.factories.celery import create_celery


celery = create_celery(create_application())


class SqlAlchemyTask(celery.Task):
    """An abstract Celery Task that ensures that the connection the the
    database is closed on task completion"""
    abstract = True

    def __call__(self, *args, **kwargs):
        try:
            return super().__call__(*args, **kwargs)
        except DatabaseError:
            SlaReportModel.session.rollback()
        finally:
            SlaReportModel.session.commit()


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
            send_async_email(msg)
        # report.to_excel(writer)
        start_time += td

    return True


def run_reports(start_time, end_time, interval='D', period=1):
    td = get_td(interval, period)

    while start_time <= end_time:
        make_sla_report_model(start_time, start_time + td)
        start_time += td

    return True


@celery.task(base=SqlAlchemyTask, name='report.tasks.make_sla_report_model')
def make_sla_report_model(start_time=None, end_time=None):
    # Check if report already exists
    if not (start_time and end_time):
        start_time = end_time = datetime.today().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        start_time -= timedelta(days=1)
    try:
        if report_exists_by_name('sla_report', start_time, end_time):
            raise AssertionError("Report is already made.")

        # Check that the data has been loaded for the report date
        if not check_src_data_loaded(start_time, end_time):
            # TODO: Have this provide the tables and dates not loaded or
            # TODO: manage loading those tables and dates...
            print("Cannot make report. Src data is not loaded.")
            raise AssertionError("Data not loaded.")

        # Check if the data exists and get data for the interval
        query = get_calls_by_direction('c_call', start_time, end_time)

        # Collate data for interval
        output_headers = [
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
            'Call Ans + 999',
            'Longest Waiting Answered'
        ]

        default_row = [
            0,              # 'I/C Presented'
            0,              # 'I/C Live Answered'
            0,              # 'I/C Abandoned'
            0,              # 'Voice Mails'
            timedelta(0),   # Answered Incoming Duration
            timedelta(0),   # Answered Wait Duration
            timedelta(0),   # Lost Wait Duration
            0,              # 'Calls Ans Within 15'
            0,              # 'Calls Ans Within 30'
            0,              # 'Calls Ans Within 45'
            0,              # 'Calls Ans Within 60'
            0,              # 'Calls Ans Within 999'
            0,              # 'Call Ans + 999'
            timedelta(0)    # 'Longest Waiting Answered'
        ]

        report_draft = {}

        for call in query:

            # Index on dialed party number
            row_name = str(call.dialed_party_number)
            row = report_draft.get(row_name, OrderedDict(zip(output_headers, default_row)))

            event_dict = {}
            # Caching events by type makes report comparisons easier
            for ev in call.events:
                event_dict[ev.event_type] = event_dict.get(ev.event_type, timedelta(seconds=0)) + ev.length

            # Event type 4 represents talking time with an agent
            talking_time = event_dict.get(4, timedelta(0))

            # Event type 10 represents a switch to voice mail
            voicemail_time = event_dict.get(10, timedelta(0))

            # Event type 5 = , 6 = , 7 =
            hold_time = sum(
                [event_dict.get(event_type, timedelta(0)) for event_type in (5, 6, 7)],
                timedelta(0)
            )
            wait_duration = call.length - talking_time - hold_time

            # A live-answered call has > 0 seconds of agent talking time
            if talking_time > timedelta(0):
                row['I/C Presented'] += 1
                row['I/C Live Answered'] += 1
                row['Answered Incoming Duration'] += talking_time
                row['Answered Wait Duration'] += wait_duration

                # Qualify calls by duration
                if wait_duration <= timedelta(seconds=15):
                    row['Calls Ans Within 15'] += 1
                elif wait_duration <= timedelta(seconds=30):
                    row['Calls Ans Within 30'] += 1
                elif wait_duration <= timedelta(seconds=45):
                    row['Calls Ans Within 45'] += 1
                elif wait_duration <= timedelta(seconds=60):
                    row['Calls Ans Within 60'] += 1
                elif wait_duration <= timedelta(seconds=999):
                    row['Calls Ans Within 999'] += 1
                else:
                    row['Call Ans + 999'] += 1

                # Update longest answered call
                if wait_duration > row['Longest Waiting Answered']:
                    row['Longest Waiting Answered'] = wait_duration

            # A voice mail is not live answered and last longer than 20 seconds
            elif voicemail_time > timedelta(seconds=20):
                row['I/C Presented'] += 1
                row['Voice Mails'] += 1
                row['Lost Wait Duration'] += call.length

            # An abandoned call is not live answered and last longer than 20 seconds
            elif call.length > timedelta(seconds=20):
                row['I/C Presented'] += 1
                row['I/C Abandoned'] += 1
                row['Lost Wait Duration'] += call.length

            report_draft[row_name] = row

        SlaReportModel.create(start_time=start_time, end_time=end_time, data=report_draft)
    except AssertionError as e:
        if e == "Data not loaded.":
            print("Data is not loaded.")
        if e == "Report is already made.":
            print("Report already created.")
        return False
    else:
        try:
            SlaReportModel.session.commit()
        # Rollback a bad session
        except DatabaseError:
            SlaReportModel.session.rollback()
        return True


def check_src_data_loaded(start_time, end_time, tables=("c_call", "c_event")):
    """
    Return True if the data is loaded for the date interval for all tables. Return False
    if not.
    :return:
    """
    table_loader = get_model("tables_loaded")
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

