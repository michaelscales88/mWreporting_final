# report/services/sla_report.py
from modules.celery_tasks import task_logger as logger
from modules.celery_worker import celery
from modules.report.models import SlaReportModel, SummarySLAReportModel
from modules.utilities.helpers import utc_now
from .reports import build_sla_data, build_summary_sla_data


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
        report = SlaReportModel.create(
            start_time=start_time, end_time=end_time, last_updated=utc_now()
        )
    else:
        report.update(last_updated=utc_now())
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

    report.update(
        data=report_data, last_updated=utc_now(), completed_on=utc_now()
    )
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
