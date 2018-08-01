# report/services/sla_report.py
from collections import OrderedDict
from datetime import timedelta, datetime

from sqlalchemy.exc import DatabaseError

from app.celery import celery, SqlAlchemyTask
from .models import SlaReportModel
from .utilities import check_src_data_loaded, report_exists_by_name, get_calls_by_direction


@celery.task(base=SqlAlchemyTask, name='report.builders.make_sla_report_model')
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
            0,  # 'I/C Presented'
            0,  # 'I/C Live Answered'
            0,  # 'I/C Abandoned'
            0,  # 'Voice Mails'
            timedelta(0),  # Answered Incoming Duration
            timedelta(0),  # Answered Wait Duration
            timedelta(0),  # Lost Wait Duration
            0,  # 'Calls Ans Within 15'
            0,  # 'Calls Ans Within 30'
            0,  # 'Calls Ans Within 45'
            0,  # 'Calls Ans Within 60'
            0,  # 'Calls Ans Within 999'
            0,  # 'Call Ans + 999'
            timedelta(0)  # 'Longest Waiting Answered'
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
