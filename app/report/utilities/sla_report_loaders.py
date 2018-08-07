# report/services/sla_report.py
import logging
from datetime import timedelta, datetime

from flask import current_app
from flask_mail import Message
from sqlalchemy.exc import DatabaseError
from sqlalchemy.sql import and_

from app.celery import celery, SqlAlchemyTask
from app.celery import get_task_logger
from ..utilities import report_exists_by_name
from ..models import SlaReportModel
from ..builders import make_sla_report


app_logger = logging.getLogger("app")
task_logger = get_task_logger(__name__)


@celery.task(base=SqlAlchemyTask, name='report.utilities.report_loader')
def report_loader(*args):
    reports_to_run = SlaReportModel.query.filter(
        and_(
            SlaReportModel.data.is_(None)
        )
    ).limit(
        current_app.config.get('MAX_INTERVAL', 10)
    ).all()
    for report in reports_to_run:
        report.update(data={"Loading": True})
        report.session.commit()

    for report in reports_to_run:
        report_data = make_sla_report(report.start_time, report.end_time)
        print("made report", report)
        report.update(data=report_data)
        try:
            report.session.commit()
        # Rollback a bad session
        except DatabaseError as err:
            report.session.rollback()
            raise err
        else:
            task_logger.info(
                "Successfully finished making report for: "
                "{start} to {end}".format(start=report.start_time, end=report.end_time)
            )
        print(report)

    # # Check the report model exists
    # report_exists = report_exists_by_name('sla_report', start_time, end_time)
    # print("get_sla_report")
    # try:
    #     # If the report does not exist make a report.
    #     # Raise AssertionError if a report is not made.
    #     if not report_exists:
    #         report_made = make_sla_report_model(start_time, end_time)
    #         print("made report:", report_made)
    #         if not report_made:
    #             raise AssertionError("Report not made.")
    #
    #     report_query = get_report_model('sla_report', start_time, end_time)
    #
    #     if not report_query:
    #         raise AssertionError("Report not found.")
    #
    #     report_frame = query_to_frame(report_query, is_report=True)
    #
    #     # Filter the report to only include desired clients
    #     if clients:
    #         report_frame = report_frame.filter(items=clients, axis=0)
    #
    #     # Make the visible index the DID extension + client name,
    #     # or just DID extension if no name exists
    #     report_frame = add_frame_alias("client", report_frame)
    #
    #     if not report_frame.empty:
    #         # Create programmatic columns and rows
    #         report_frame = make_summary(report_frame)
    #         report_frame = compute_avgs(report_frame)
    #
    #         # Filter out columns containing raw data
    #         columns = display_columns('sla_report')
    #         report_frame = report_frame[columns]
    #
    # except AssertionError as e:
    #     if e == "Report not made.":
    #         print("Error: report not made")
    #     if e == "Report not found.":
    #         print("Error: report not found.")
    #
    #     return empty_report()
    # else:
    #     # Prettify percentages
    #     return report_frame.applymap(format_df)


@celery.task(base=SqlAlchemyTask, name='report.utilities.make_sla_report_model')
def make_sla_report_model(*args, start_time=None, end_time=None):
    # Check if report already exists
    if not (start_time and end_time):
        start_time = end_time = datetime.today().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        start_time -= timedelta(days=1)
    try:
        if report_exists_by_name('sla_report', start_time, end_time):
            raise AssertionError("Report is already made.")

        report_data = make_sla_report(start_time, end_time)
        if report_data:
            SlaReportModel.create(start_time=start_time, end_time=end_time, data=report_data)
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


def email_reports(start_time, end_time, interval='D', period=1):
    td = get_td(interval, period)
    filename = "test_report.xlsx"
    # output = io.BytesIO()
    # writer = pd.ExcelWriter(filename,
    #                         engine='xlsxwriter',
    #                         datetime_format='mmm d yyyy hh:mm:ss',
    #                         date_format='mmmm dd yyyy')
    while start_time <= end_time:
        report = report_loader(start_time, start_time + td)
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
            # send_async_email(msg)
        # report.to_excel(writer)
        start_time += td

    return True


def run_reports(start_time, end_time, interval='D', period=1):
    td = get_td(interval, period)

    while start_time <= end_time:
        make_sla_report_model(start_time, start_time + td)
        start_time += td

    return True
