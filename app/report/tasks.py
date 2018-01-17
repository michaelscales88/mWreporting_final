# report/tasks.py
from celery.schedules import crontab
import pandas as pd
import numpy as np
from collections import OrderedDict
from datetime import timedelta
from flask import g, abort
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import and_


from app import celery
from app.util.tasks import get_model, query_to_frame, display_columns
from app.client.tasks import add_client_alias
from .models import SlaData


def add_scheduled_tasks(app):
    # TODO automatically make yesterdays report at 12:01 AM
    # app.config['CELERYBEAT_SCHEDULE']['test'] = {
    #     'task': 'app.data.tasks.load_data',
    #     'schedule': crontab(minute='*/15'),
    #     'args': ('date1', 'date2')
    # }
    pass


def get_calls_by_direction(session, table_name, start_time, end_time, call_direction=1):
    table = get_model(table_name)
    return session.query(table).filter(
        and_(
            table.start_time >= start_time,
            table.end_time <= end_time,
            table.call_direction == call_direction
        )
    )


def report_exists(session, table_name, start_time, end_time):
    return False if get_report(session, table_name, start_time, end_time) is None else True


def get_report(session, table_name, start_time, end_time):
    table = get_model(table_name)
    return session.query(table).filter(
        and_(
            table.start_time == start_time,
            table.end_time == end_time,
        )
    ).first()


class SqlAlchemyTask(celery.Task):
    """An abstract Celery Task that ensures that the connection the the
    database is closed on task completion"""
    abstract = True

    def __call__(self, *args, **kwargs):
        # try:
        #     return super().__call__(*args, **kwargs)
        # except DatabaseError:
        #     app_meta_session.rollback()
        # finally:
        #     app_meta_session.commit()
        pass

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        # app_meta_session.remove()
        # print(task_id, ' closed sessions: ', app_meta_session)
        pass


def test_report(start_date, end_date, report_id=None):
    """
    Get report from id if it exists or make the report for the interval
    """
    # Add report model stuff here
    print('for sure i did this')
    return [{
        'id': 'Test Successful',
        'date': start_date,
        'report': end_date,
        'notes': report_id
    }], None, 200


# @celery.task(base=SqlAlchemyTask, max_retries=10, default_retry_delay=60)
# def fetch_or_make_report(start_time, end_time):
#     """
#     Get report from id if it exists or make the report for the interval
#     """
#     from datetime import timedelta
#     report_id = SLAReport.query.filter(
#         and_(
#             SLAReport.start_time == start_time,
#             SLAReport.end_time == end_time,
#         )
#     )
#     report = SLAReport.query.get_or(report_id)
#     if report:
#         pass
#     # Add report model stuff here
#     print('for sure i did this')
#     return [{
#         'id': 'Test Successful',
#         'date': start_time,
#         'report': end_time,
#         'notes': report
#     }]


def make_report(session, start_time, end_time):
    # Check if report already exists
    if report_exists(session, 'sla_report', start_time, end_time):
        print('found a completed report')
        return True

    # Check if the data exists and get data for the interval
    print('creating report')
    query = get_calls_by_direction(session, 'c_call', start_time, end_time)

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

    new_record = SlaData(start_time=start_time, end_time=end_time, data=report_draft)
    session.add(new_record)

    print('completed report')
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


def report_task(task_name, start_time=None, end_time=None, clients=None, id=None):
    try:
        result = None
        if task_name == 'get' and start_time and end_time:

            # Get the stored report for the date interval.
            # This report is the aggregated raw data indexed by DID Extension.
            query = get_report(g.local_session, 'sla_report', start_time, end_time)
            frame = query_to_frame(query, is_report=True)

            # Filter the report to only include desired clients
            if clients:
                frame = frame.filter(items=clients, axis=0)

            # Make the visible index the DID extension + client name,
            # or just DID extension if no name exists
            frame = add_client_alias(frame)

            # Create programmatic columns and rows
            frame = make_summary(frame)
            frame = compute_avgs(frame)

            # Filter out columns containing raw data
            columns = display_columns('sla_report')
            frame = frame[columns]

            # Prettify percentages
            result = frame.applymap(format_df)
        elif task_name == 'load':
            print('trying to make a report')
            result = make_report(g.local_session, start_time, end_time)

        if result is None:
            raise NoResultFound()
    except NoResultFound:
        result = None
        status = 404
        abort(status)
    else:
        status = 200

    return result, status
