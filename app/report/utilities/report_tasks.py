# report/services/sla_report.py
import datetime
from flask import current_app
from sqlalchemy.sql import or_

from app.celery import celery
from app.celery_tasks import task_logger as logger
from ..builders import build_sla_data, build_summary_sla_data
from ..models import SlaReportModel, SummarySLAReportModel


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

    report.update(data=report_data, completed_on=datetime.datetime.utcnow())
    SlaReportModel.session.commit()
    logger.warning(
        "Completed: Make SLA report - {start} to {end}".format(
            start=start_time, end=end_time
        )
    )
    return True


@celery.task(name='report.utilities.report_loader')
def report_loader(*args):
    logger.warning("Started: Report loader")
    limit = current_app.config.get('MAX_INTERVAL', 6)
    reports_query = SlaReportModel.query.filter(
        SlaReportModel.completed_on.is_(None)
    )

    reports_query = reports_query.filter(
        or_(
            SlaReportModel.last_updated.is_(None),
            SlaReportModel.last_updated < datetime.datetime.utcnow() + datetime.timedelta(minutes=limit),
        )
    )

    # Minimize stressing the system by preventing massive queries
    reports_query = reports_query.limit(limit).all()

    reports_to_make = []
    for report_model in reports_query:
        report_model.update(last_updated=datetime.datetime.utcnow().replace(microsecond=0))
        reports_to_make.append((report_model.start_time, report_model.end_time))
    SlaReportModel.session.commit()

    if not len(reports_query) > 0:
        logger.info("No reports to load.")
        return "Success: No reports to load."

    for start_time, end_time in reports_to_make:
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


@celery.task(name='report.utilities.report_scheduler')
def report_scheduler(*args):
    logger.warning("Started: Report scheduler.")
    start = datetime.datetime.strptime("08/01/18 07:00", "%m/%d/%y %H:%M")
    end = start + datetime.timedelta(days=30)
    while start < end:
        end_dt = start + datetime.timedelta(hours=12)
        if SlaReportModel.get(start, end_dt) is None:
            SlaReportModel.create(start_time=start, end_time=end_dt)
        start = end_dt
    SlaReportModel.session.commit()
    logger.warning("Completed: Report scheduler.")


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

    report.update(data=report_data, completed_on=datetime.datetime.utcnow().replace(microsecond=0))
    SummarySLAReportModel.session.commit()
    logger.warning(
        "Successfully finished making report for: "
        "{start} to {end}".format(start=start_time, end=end_time)
    )


@celery.task(name='report.utilities.summary_report_loader')
def summary_report_loader(*args):
    logger.warning("Started: Summary report loader.")
    summary_report_query = SummarySLAReportModel.query.filter(
        SummarySLAReportModel.completed_on.is_(None)
    )

    report_model = summary_report_query.filter(
        or_(
            SummarySLAReportModel.last_updated.is_(None),
            SummarySLAReportModel.last_updated < (
                datetime.datetime.utcnow() + datetime.timedelta(minutes=2)
            )
        )
    ).first()

    if report_model:
        start_time = report_model.start_time
        end_time = report_model.end_time
        frequency = report_model.frequency
        report_model.update(last_updated=datetime.datetime.utcnow().replace(microsecond=0))
        SummarySLAReportModel.session.commit()

        if not make_summary_sla_report(
            start_time=start_time, end_time=end_time, frequency=frequency
        ):
            logger.error(
                "Error: Failed to make report for: "
                "{start} to {end}".format(start=start_time, end=end_time)
            )
    else:
        logger.info("No summary reports to run.")
    logger.warning("Completed: Summary report loader.")


def email_reports(start_time, end_time, interval='D', period=1):
    # td = get_td(interval, period)
    # filename = "test_report.xlsx"
    # # output = io.BytesIO()
    # # writer = pd.ExcelWriter(filename,
    # #                         engine='xlsxwriter',
    # #                         datetime_format='mmm d yyyy hh:mm:ss',
    # #                         date_format='mmmm dd yyyy')
    # while start_time <= end_time:
    #     report = report_loader(start_time, start_time + td)
    #     with report as report:
    #         print(report)
    #         msg = Message(
    #             "Report Test",
    #             recipients=[current_app.config['MAIL_USERNAME']],
    #             # attachments=Attachment(
    #             #     filename=filename,
    #             #     data=report.to_excel(writer)
    #             # )
    #         )
    #         msg.attach(filename, "xlsx", export_excel(report))
    #         # send_async_email(msg)
    #     # report.to_excel(writer)
    #     start_time += td
    return True
