from collections import OrderedDict
from datetime import timedelta
from sqlalchemy.exc import DatabaseError
from sqlalchemy.sql import and_
from sqlalchemy.orm.exc import NoResultFound

from app import celery

from .models import SLAReport, Client, app_meta_session


_mmap = {
    "sla_report": SLAReport,
    "client": Client
}


def get_report_headers(model=None):
    if model in _mmap.keys():
        return _mmap.get(model, None).__repr_attrs__
    return None


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


def report_dispatch(start_time, end_time, report_id=None):
    """
    Get report from id if it exists or make the report for the interval
    """
    report = None
    try:
        # Check if the the report exists
        if report_id:
            report = SLAReport.query.get_or(report_id)
        else:
            report = SLAReport.query.filter(
                and_(
                    SLAReport.start_time == start_time,
                    SLAReport.end_time == end_time,
                )
            )

        # If none exists make one
        if not report:

            print(report)
            report = "Success"

    except (DatabaseError, NoResultFound):
        app_meta_session.rollback()
    else:
        app_meta_session.commit()
    finally:
        app_meta_session.remove()
    # Add report model stuff here
    print('for sure i did this')
    return [{
        'id': 'Test Successful',
        'date': start_time,
        'report': end_time,
        'notes': report
    }], None, 200


class SqlAlchemyTask(celery.Task):
    """An abstract Celery Task that ensures that the connection the the
    database is closed on task completion"""
    abstract = True

    def __call__(self, *args, **kwargs):
        try:
            return super().__call__(*args, **kwargs)
        except DatabaseError:
            app_meta_session.rollback()
        finally:
            app_meta_session.commit()

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        app_meta_session.remove()
        print(task_id, ' closed sessions: ', app_meta_session)


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


from flask import current_app
from datetime import time

from app import celery

from .common import *


@celery.task
def report_task(start, end):
    success = False

    # Create a pyexcel table with the appropriate defaults by column name
    prepared_report = make_pyexcel_table(
        current_app.config['sla_report_headers'],
        list(current_app.config['CLIENTS']),
        current_app.config['sla_default_row']
    )

    try:
        session.query(
            CallTable,
            EventTable.event_type,
            EventTable.start_time.label('event_start_time'),
            EventTable.end_time.label('event_end_time')
        ).join(
            EventTable
        ).filter(
            and_(
                CallTable.start_time >= start,
                CallTable.end_time <= end,
                CallTable.call_direction == 1
            )
        )
        record_query = get_records(db_session, start, end)
        record_list = record_query.all()

        # Index the query. Group columns from EventTable (c_event) to the call from CallTable (c_call)
        cached_results = prepare_records(record_list)

        # Consume query data
        report = process_report(prepared_report, cached_results)
        report.name = 'sla_report'

        for rd in current_app.config['sla_row_data']:
            make_programmatic_column(report, **rd)

        # Stringify each cell
        format_table(report)

        cache_report(db_session, start, end, report)

    except Exception as e:
        print(e)
        db_session.rollback()
    else:
        db_session.commit()
        # Set success flag on commit
        success = True
    finally:
        db_session.remove()

    return success


def prepare_records(record_list):
    """
    Group calls by event type on the Event Table
    Use the grouped event types to give the call properties
    E.g. Interval of 0 for event type 4 means that the call never had Talking time == Unanswered call
    :param record_list:
    :return: OrderedDict. Key: CallTable Values: Sum of intervals grouped by event type
    """
    cached_results = OrderedDict()
    for call, event_type, start, end in record_list:

        cached_result = cached_results.get(call)

        if cached_result:
            # Get the event_type from the call
            cached_event = cached_result.get(event_type)

            # Update or create the event for the call
            if cached_event:
                cached_event += end - start
            else:
                cached_event = end - start

            cached_result[event_type] = cached_event
        else:
            # Create a cache if one does not exist
            cached_result = {
                event_type: end - start
            }

        # Update the cached results with the accumulated event
        cached_results[call] = cached_result
    return cached_results


def process_report(in_process_report, records):
    for call, events in records.items():

        # Dialed party number is the client
        row_name = str(call.dialed_party_number)

        if row_name in in_process_report.rownames and time(hour=7) <= call.start_time.time() <= time(hour=19):
            call_duration = call.end_time - call.start_time
            talking_time = events.get(4, timedelta(0))
            voicemail_time = events.get(10, timedelta(0))
            hold_time = sum(
                [events.get(event_type, timedelta(0)) for event_type in (5, 6, 7)],
                timedelta(0)
            )
            wait_duration = call_duration - talking_time - hold_time

            # A live-answered call has > 0 seconds of agent talking time
            if talking_time > timedelta(0):
                in_process_report[row_name, 'I/C Presented'] += 1
                in_process_report[row_name, 'I/C Live Answered'] += 1
                in_process_report[row_name, 'Average Incoming Duration'] += talking_time
                in_process_report[row_name, 'Average Wait Answered'] += wait_duration

                # Qualify calls by duration
                if wait_duration <= timedelta(seconds=15):
                    in_process_report[row_name, 'Calls Ans Within 15'] += 1

                elif wait_duration <= timedelta(seconds=30):
                    in_process_report[row_name, 'Calls Ans Within 30'] += 1

                elif wait_duration <= timedelta(seconds=45):
                    in_process_report[row_name, 'Calls Ans Within 45'] += 1

                elif wait_duration <= timedelta(seconds=60):
                    in_process_report[row_name, 'Calls Ans Within 60'] += 1

                elif wait_duration <= timedelta(seconds=999):
                    in_process_report[row_name, 'Calls Ans Within 999'] += 1

                else:
                    in_process_report[row_name, 'Call Ans + 999'] += 1

                if wait_duration > in_process_report[row_name, 'Longest Waiting Answered']:
                    in_process_report[row_name, 'Longest Waiting Answered'] = wait_duration

            # A voice mail is not live answered and last longer than 20 seconds
            elif voicemail_time > timedelta(seconds=20):
                in_process_report[row_name, 'I/C Presented'] += 1
                in_process_report[row_name, 'Voice Mails'] += 1
                in_process_report[row_name, 'Average Wait Lost'] += call_duration

            # An abandoned call is not live answered and last longer than 20 seconds
            elif call_duration > timedelta(seconds=20):
                in_process_report[row_name, 'I/C Presented'] += 1
                in_process_report[row_name, 'I/C Abandoned'] += 1
                in_process_report[row_name, 'Average Wait Lost'] += call_duration

    return in_process_report
