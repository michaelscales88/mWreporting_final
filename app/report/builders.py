# report/services/sla_report.py
import logging
from collections import OrderedDict, Counter
from datetime import timedelta
from sqlalchemy.sql import and_

from .models import TablesLoadedModel, CallTableModel, SlaReportModel


logger = logging.getLogger("app")

HEADERS = [
    'I/C Presented',
    'I/C Live Answered',
    'I/C Lost',
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

DEFAULT_ROW_VALS = [
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

DEFAULT_ROW = OrderedDict(zip(HEADERS, DEFAULT_ROW_VALS))


def build_sla_data(start_time, end_time):
    logger.info(
        "Started: Building SLA report data {start} to {end}".format(
            start=start_time, end=end_time
        )
    )
    # Check that the data has been loaded for the report date
    if not TablesLoadedModel.interval_is_loaded(start_time, end_time):
        logger.warning("Data not loaded for report interval.\n"
                       "Attempting to load data.")
        # TODO: implement this

    inbound_calls = CallTableModel.query.filter(
        and_(
            CallTableModel.start_time >= start_time,
            CallTableModel.end_time <= end_time,
            CallTableModel.call_direction == 1
        )
    ).all()

    # Collate data for interval
    sla_data = {}
    for call in inbound_calls:

        # Index on dialed party number
        row_name = str(call.dialed_party_number)
        row = sla_data.get(row_name, DEFAULT_ROW)

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
            row['I/C Lost'] += 1
            row['Lost Wait Duration'] += call.length

        sla_data[row_name] = row

    # Remove empty rows
    for row_name in [
        row_name
        for row_name in sla_data.keys()
        if sla_data[row_name]['I/C Presented'] == 0
    ]:
        sla_data.pop(row_name)

    logger.info(
        "Completed: Building SLA report data {start} to {end}".format(
            start=start_time, end=end_time
        )
    )
    return sla_data


def build_summary_sla_data(start_time, end_time, interval):
    logger.info(
        "Started: Building SLA summary report data {start} to {end}".format(
            start=start_time, end=end_time
        )
    )

    if not SlaReportModel.interval_is_loaded(start_time, end_time, interval):
        logger.warning("Data not loaded for report interval.\n"
                       "Attempting to load data.")
        # TODO: implement this
        return "Error: SLA reports are not loaded for the interval."

    summary_sla_data = {}
    while start_time < end_time:
        end_dt = start_time + interval
        report = SlaReportModel.get(start_time, end_dt)
        if not report:
            logger.warning("Report not created for report interval.\n"
                           "Attempting to load data.")
            SlaReportModel.create(start_time=start_time, end_time=end_dt)
            SlaReportModel.session.commit()
            # TODO: implement this
            return "Error: a SLA report could not be located for {start} to {end}.".format(
                start=start_time, end=end_dt
            )

        if not report.data:
            logger.warning(
                "Error: a SLA report with finished data could not "
                "be located for {start} to {end}.".format(
                    start=start_time, end=end_dt
                )
            )
            # TODO: implement this
            return "Error: data is not loaded for report"

        dt_row_name = "{date} {start} to {end}".format(
            date=start_time.date(), start=start_time.time(), end=end_dt.time()
        )
        for row_name in report.data.keys():
            summary = summary_sla_data.get(row_name, {})
            summary[dt_row_name] = report.data[row_name]
            summary_sla_data[row_name] = summary

        start_time = end_dt

    logger.info(
        "Completed: Building SLA report data {start} to {end}".format(
            start=start_time, end=end_time
        )
    )
    return summary_sla_data
