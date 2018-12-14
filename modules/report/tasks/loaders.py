# data/services/loaders.py
import datetime
from json import dumps

from flask import current_app
from sqlalchemy.sql import func

from modules.report.models import (
    TablesLoadedModel, CallTableModel, EventTableModel,
    SlaReportModel
)
from .reports import build_sla_data
from modules.report.utilities import get_external_session
from modules.utilities.helpers import utc_now
from modules.worker import task_logger as logger


def call_data_loader(*args):
    logger.warning("Start: Call Data loader.")

    # Args
    load_date = args[0]
    if not load_date or isinstance(load_date, datetime.date):
        logger.warning(
            "Failed to start call data loader [ {} ].".format(load_date)
        )
        return
    else:
        logger.warning(
            "Starting call data loader [ {} ].".format(load_date)
        )

    ext_uri = current_app.config.get('EXTERNAL_DATABASE_URI')
    if not ext_uri:
        logger.error("Error: External database connection not set.\n"
                     "Add 'EXTERNAL_DATABASE_URI' to your config with\n"
                     "the address to your database.")
        return "Error: No external connection available."

    tl_model = TablesLoadedModel.find(load_date)
    if tl_model and tl_model.calls_loaded:
        logger.warning(
            "Call data for [ {} ] already loaded.".format(load_date)
        )
        return True

    try:
        ext_session = get_external_session(ext_uri)

        # Get the data from the source database
        results = ext_session.query(CallTableModel).filter(
            func.DATE(CallTableModel.start_time) == load_date
        ).all()
        ext_session.remove()

        # Add the records from the external database to the local
        # database. Add record by record grouped by date. Check if
        # the record exists before adding.
        for result in results:
            ext_primary_key = result.get('call_id')
            if not ext_primary_key:
                logger.error("Could not identify primary key for foreign record.\n"
                             "{dump}".format(dump=dumps(result, indent=2, default=str)))
                continue

            record = CallTableModel.find(ext_primary_key)
            if not record:
                CallTableModel.create(
                    **{
                        entry: result[entry]
                        for entry in result.keys() if entry != '_sa_instance_state'
                    }
                )
            else:
                logger.warning("Record Exists: {rec}".format(rec=record))

        tl_model = TablesLoadedModel.find(load_date)
        if load_date < utc_now().date():
            tl_model.update(calls_loaded=True)
        tl_model.update(last_updated=utc_now())
        tl_model.session.commit()
        tl_model.session.remove()
    except Exception as err:
        logger.error("Encountered an error.", err)
        raise err
    else:
        logger.warning(
            "Completed call data loader [ {} ].".format(load_date)
        )
        return True


def event_data_loader(*args):
    logger.warning("Start: Event data loader.")

    # Args
    load_date = args[0]
    if not load_date or isinstance(load_date, datetime.date):
        logger.warning(
            "Failed to start event data loader [ {} ].".format(load_date)
        )
        return
    else:
        logger.warning(
            "Starting event data loader [ {} ].".format(load_date)
        )

    ext_uri = current_app.config.get('EXTERNAL_DATABASE_URI')
    if not ext_uri:
        logger.error("Error: External database connection not set.\n"
                     "Add 'EXTERNAL_DATABASE_URI' to your config with\n"
                     "the address to your database.")
        return "Error: No external connection available."

    tl_model = TablesLoadedModel.find(load_date)
    if tl_model and tl_model.events_loaded:
        logger.warning(
            "Event data for [ {} ] already loaded.".format(load_date)
        )
        return True

    try:
        ext_session = get_external_session(ext_uri)

        # Get the data from the source database
        results = ext_session.query(EventTableModel).filter(
            func.DATE(EventTableModel.start_time) == load_date
        ).all()
        ext_session.remove()

        # Add the records from the external database to the local
        # database. Add record by record grouped by date. Check if
        # the record exists before adding.
        for result in results:
            ext_primary_key = result.get('event_id')
            if not ext_primary_key:
                logger.error("Could not identify primary key for foreign record.\n"
                             "{dump}".format(dump=dumps(result, indent=2, default=str)))
                continue

            record = EventTableModel.find(ext_primary_key)
            if not record:
                EventTableModel.create(
                    **{
                        entry: result[entry]
                        for entry in result.keys() if entry != '_sa_instance_state'
                    }
                )
            else:
                logger.warning("Record Exists: {rec}".format(rec=record))

        if load_date < utc_now().date():
            tl_model.update(events_loaded=True)
        tl_model.update(last_updated=utc_now())
        tl_model.session.commit()
        tl_model.session.remove()
    except Exception as err:
        logger.error("Encountered an error.", err)
        raise err
    else:
        logger.warning(
            "Completed event data loader [ {} ].".format(load_date)
        )
        return True


def report_loader(*args):
    logger.warning("Started: Report loader.")

    # Args
    start_time = args[0]
    end_time = args[1]

    if (
        not all([start_time, end_time])
        and not isinstance(start_time, datetime.datetime)
        and not isinstance(end_time, datetime.datetime)
    ):
        logger.error(
            "Error: Report times: {start} and {end} are"
            "not both provided, or they're not datetime format.\n".format(
                start=start_time, end=end_time
            )
        )
        logger.error(
            "Failed to start report data loader [ {} - {} ].".format(
                start_time, end_time
            )
        )
        return
    else:
        logger.warning(
            "Starting report data loader [ {} - {} ].".format(
                start_time, end_time
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


# def make_summary_sla_report(*args, start_time=None, end_time=None, frequency=None):
#     logger.warning(
#         "Started: Make SLA summary report - {start} to {end}".format(
#             start=start_time, end=end_time
#         )
#     )
#     if not (start_time and end_time and frequency):
#         logger.error(
#             "Error: Report times or frequency: {start}, {end}, "
#             "or {frequency} were not provided.\n".format(
#                 start=start_time, end=end_time, frequency=frequency
#             )
#         )
#         return
#
#     report = SummarySLAReportModel.get(start_time, end_time, frequency)
#     if not report:
#         report = SummarySLAReportModel.create(
#             start_time=start_time, end_time=end_time, frequency=frequency
#         )
#         report.session.commit()
#
#     if report.data:
#         logger.info(
#             "Report exists for {start} to {end} over interval "
#             "{interval}.\n".format(
#                 start=report.start_time, end=report.end_time, interval=report.interval
#             )
#         )
#         return
#
#     report_data = build_summary_sla_data(start_time, end_time, report.interval)
#
#     if not report_data:
#         logger.error(
#             "Error: Could not build report for: {start} and {end} "
#             "over interval {interval}.\n".format(
#                 start=start_time, end=end_time, interval=report.interval
#             )
#         )
#         return
#
#     if isinstance(report_data, str):
#         logger.error(report_data)
#         return
#
#     report.update(data=report_data, completed_on=utc_now())
#     report.session.commit()
#     report.session.remove()
#     logger.warning(
#         "Successfully finished making report for: "
#         "{start} to {end}".format(start=start_time, end=end_time)
#     )
