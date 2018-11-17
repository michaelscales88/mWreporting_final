# report/services/sla_report.py
import datetime
from sqlalchemy.sql import or_, and_

from modules.core import utc_now
from modules.celery_worker import celery
from modules.celery_tasks import task_logger as logger
from modules.report.builders import build_sla_data, build_summary_sla_data
from modules.report.models import SlaReportModel, SummarySLAReportModel


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
    SlaReportModel.session.commit()
    SlaReportModel.session.remove()
    logger.warning(
        "Completed: Make SLA report - {start} to {end}".format(
            start=start_time, end=end_time
        )
    )
    return True


@celery.task(name='report.utilities.report_loader')
def report_loader(*args):
    logger.warning("Started: Report loader {}".format(utc_now()))

    # TODO: Convert to a working query
    next_report = None

    for report in SlaReportModel.all():
        print(report)
        if not report.completed_on:
            if report.last_updated:
                if report.last_updated < utc_now() - datetime.timedelta(minutes=5):
                    next_report = report
                    break
            else:
                # Untouched report
                next_report = report
                break

    if next_report:
        next_report.update(last_updated=utc_now())
        next_report.session.commit()
    else:
        logger.info("No reports to load.")
        return "Success: No reports to load."

    start_time = next_report.start_time
    end_time = next_report.end_time

    if make_sla_report(start_time=start_time, end_time=end_time):
        logger.info(
            "Successfully finished making report for: "
            "{start} to {end}".format(start=start_time, end=end_time)
        )
    else:
        logger.error(
            "Error: Failed to make report for: "
            "{start} to {end}".format(start=start_time, end=end_time)
        )

    logger.warning("Completed: Report loader")


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


@celery.task(name='report.utilities.summary_report_loader')
def summary_report_loader(*args):
    logger.warning("Started: Summary report loader {}".format(utc_now()))
    next_report = SummarySLAReportModel.query.filter(
        or_(
            SummarySLAReportModel.last_updated == None,  # If the report has never been run
            and_(
                # If the report was run, but didn't succeed
                SummarySLAReportModel.completed_on == None,
                SummarySLAReportModel.last_updated < (utc_now() - datetime.timedelta(minutes=5))
            )
        )
    ).first()

    if not next_report:
        logger.info("No summary reports to run.")
        return "Success: No summary reports to load."
    else:
        next_report.update(last_updated=utc_now())
        next_report.session.commit()

    start_time = next_report.start_time
    end_time = next_report.end_time
    frequency = next_report.frequency

    if not make_summary_sla_report(
        start_time=start_time, end_time=end_time, frequency=frequency
    ):
        logger.error(
            "Error: Failed to make report for: "
            "{start} to {end}".format(start=start_time, end=end_time)
        )
    logger.warning("Completed: Summary report loader.")
