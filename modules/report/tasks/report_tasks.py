# report/services/sla_report.py
# report/services/sla_report.py
from collections import OrderedDict
from datetime import timedelta

from sqlalchemy.sql import and_

from modules.celery_tasks import task_logger as logger
from modules.celery_worker import celery
from modules.utilities.helpers import utc_now
from modules.report.models import SlaReportModel, SummarySLAReportModel, TablesLoadedModel, CallTableModel


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


def build_sla_data(start_time, end_time):
    logger.info(
        "Started: Building SLA report data {start} to {end}".format(
            start=start_time, end=end_time
        )
    )
    # Check that the data has been loaded for the report date
    if not TablesLoadedModel.interval_is_loaded(start_time, end_time):
        logger.warning("Data not loaded for report interval.\n"
                       "Requesting to load data and will try again later.")
        TablesLoadedModel.add_interval(start_time, end_time)
        return

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
        row = sla_data.setdefault(row_name, OrderedDict(zip(HEADERS, DEFAULT_ROW_VALS)))

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
        # TODO: implement scheduling the reports needed for the interval
        return "Exiting: Need to create reports first"

    summary_sla_data = {}
    while start_time < end_time:
        end_dt = start_time + interval
        report = SlaReportModel.get(start_time, end_dt)
        if not report:
            logger.warning("Report not created for report interval.\n"
                           "Attempting to load data.")
            SlaReportModel.create(start_time=start_time, end_time=end_dt)
            SlaReportModel.session.commit()
            SlaReportModel.session.close()

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


@celery.task(name='report.utilities.make_sla_report')
def make_sla_report(*args, start_time=None, end_time=None):
    logger.warning(
        "Started: Make SLA report - {start} to {end}".format(
            start=start_time, end=end_time
        )
    )
    if not (start_time and end_time):
        logger.error(
            "Error: Report times: {start} and {end} are"
            "not both provided.\n".format(
                start=start_time, end=end_time
            )
        )
        return False

    report = SlaReportModel.get(start_time, end_time)
    if not report:
        report = SlaReportModel.create(start_time=start_time, end_time=end_time)
        report.session.commit()

    if report.data:
        logger.info(
            "Report exists for {start} to {end}.\n".format(
                start=start_time, end=end_time
            )
        )
        return True

    report_data = build_sla_data(start_time, end_time)

    if not report_data:
        logger.error(
            "Error: Could not build report for: {start} and {end}.\n".format(
                start=start_time, end=end_time
            )
        )
        return False

    report.update(data=report_data, completed_on=utc_now())
    report.session.commit()
    report.session.remove()
    logger.warning(
        "Completed: Make SLA report - {start} to {end}".format(
            start=start_time, end=end_time
        )
    )
    return True


@celery.task(name='report.utilities.make_summary_sla_report')
def make_summary_sla_report(*args, start_time=None, end_time=None, frequency=None):
    logger.warning(
        "Started: Make SLA summary report - {start} to {end}".format(
            start=start_time, end=end_time
        )
    )
    if not (start_time and end_time and frequency):
        logger.error(
            "Error: Report times or frequency: {start}, {end}, "
            "or {frequency} were not provided.\n".format(
                start=start_time, end=end_time, frequency=frequency
            )
        )
        return

    report = SummarySLAReportModel.get(start_time, end_time, frequency)
    if not report:
        report = SummarySLAReportModel.create(
            start_time=start_time, end_time=end_time, frequency=frequency
        )
        report.session.commit()

    if report.data:
        logger.info(
            "Report exists for {start} to {end} over interval "
            "{interval}.\n".format(
                start=report.start_time, end=report.end_time, interval=report.interval
            )
        )
        return

    report_data = build_summary_sla_data(start_time, end_time, report.interval)

    if not report_data:
        logger.error(
            "Error: Could not build report for: {start} and {end} "
            "over interval {interval}.\n".format(
                start=start_time, end=end_time, interval=report.interval
            )
        )
        return

    if isinstance(report_data, str):
        logger.error(report_data)
        return

    report.update(data=report_data, completed_on=utc_now())
    report.session.commit()
    report.session.remove()
    logger.warning(
        "Successfully finished making report for: "
        "{start} to {end}".format(start=start_time, end=end_time)
    )
