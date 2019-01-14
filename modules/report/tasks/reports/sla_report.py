# report/services/sla_report.py
from collections import OrderedDict
from datetime import timedelta

from sqlalchemy.sql import and_

from modules.worker import task_logger as logger
from modules.report.models import CallTableModel, EventTableModel, SlaReportModel


def build_sla_data(session, start_time, end_time):
    logger.warning(
        "Started: Building SLA report data {start} to {end}".format(
            start=start_time, end=end_time
        )
    )

    inbound_calls = session.query(CallTableModel).filter(
        and_(
            CallTableModel.start_time >= start_time,
            CallTableModel.start_time <= end_time,
            CallTableModel.call_direction == 1
        )
    ).all()

    # TODO: start here
    # Collate data for interval
    col_data = {}
    for call in inbound_calls:

        # Index on dialed party number
        row_name = str(call.dialed_party_number)
        row = OrderedDict(SlaReportModel.default_row())

        event_dict = {}
        events = session.query(EventTableModel).filter_by(call_id=call.call_id).all()

        # Caching events by type makes report comparisons easier
        for ev in events:
            event_type = event_dict.get(ev.event_type, timedelta(seconds=0))
            event_dict[ev.event_type] = event_type + ev.length

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
            row['I/C Lost'] += 1
            row['Lost Wait Duration'] += call.length

        col_data[row_name] = row

    # Remove empty rows
    for row_name in [
        row_name
        for row_name in col_data.keys()
        if col_data[row_name]['I/C Presented'] == 0
    ]:
        col_data.pop(row_name)

    logger.info(
        "Completed: Building SLA report data {start} to {end}".format(
            start=start_time, end=end_time
        )
    )
    return col_data
