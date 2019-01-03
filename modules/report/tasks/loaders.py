# data/services/loaders.py
import datetime
from json import dumps

from flask import current_app
from sqlalchemy.exc import DatabaseError
from sqlalchemy.sql import func

from modules.extensions import get_session
from modules.report.models import (
    TablesLoadedModel, CallTableModel, EventTableModel,
    SlaReportModel
)
from modules.report.utilities import get_external_session
from modules.utilities.helpers import utc_now
from modules.worker import task_logger as logger
from .reports import build_sla_data


def load_call_data(session, results):
    for r in results:
        if not r.call_id:
            logger.error("Could not identify primary key for foreign record.\n"
                         "{dump}".format(dump=dumps(r, indent=2, default=str)))
            continue

        existing_rec = CallTableModel.find(r.call_id)
        if existing_rec:
            logger.warning("Record Exists: {rec}".format(rec=existing_rec))
            continue

        session.add(
            CallTableModel(
                call_id=r.call_id,
                call_direction=r.call_direction,
                calling_party_number=r.calling_party_number,
                dialed_party_number=r.dialed_party_number,
                start_time=r.start_time,
                end_time=r.end_time,
                caller_id=r.caller_id,
                inbound_route=r.inbound_route
            )
        )


def load_event_data(session, results):
    for r in results:
        if not r.event_id:
            logger.error("Could not identify primary key for foreign record.\n"
                         "{dump}".format(dump=dumps(r, indent=2, default=str)))
            continue

        existing_rec = EventTableModel.find(r.event_id)
        if existing_rec:
            logger.warning("Record Exists: {rec}".format(rec=existing_rec))
            continue

        session.add(
            EventTableModel(
                event_id=r.event_id,
                event_type=r.event_type,
                calling_party=r.calling_party,
                receiving_party=r.receiving_party,
                hunt_group=r.hunt_group,
                is_conference=r.is_conference,
                start_time=r.start_time,
                end_time=r.end_time,
                call_id=r.call_id,
            )
        )


def call_data_loader(*args):
    logger.warning("Start: Call Data loader.")

    # Args
    load_date = args[0]

    if not isinstance(load_date, datetime.date):
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
        return

    session = get_session(current_app)[1]()

    tl_model = TablesLoadedModel.worker_find(session, load_date)

    if not tl_model:
        tl_model = TablesLoadedModel(loaded_date=load_date)
        session.add(tl_model)
        session.commit()

    if tl_model and tl_model.calls_loaded:
        logger.warning(
            "Call data for [ {} ] already loaded.".format(load_date)
        )
        return

    # Get the data from the source database
    ext_session = get_external_session(ext_uri)
    try:
        results = ext_session.query(CallTableModel).filter(
            func.DATE(CallTableModel.start_time) == load_date
        ).all()
    except DatabaseError:
        logger.error("Failed to get records from source database.")
    else:
        # Insert data into target database
        try:
            load_call_data(session, results)

            session.commit()
        except DatabaseError:
            logger.error("Error committing call records to target database.")
            session.rollback()

    # Update the system that the interval is loaded
    if load_date < utc_now().date():
        tl_model.calls_loaded = True
    tl_model.last_updated = utc_now()
    session.add(tl_model)
    session.commit()

    logger.warning(
        "Completed call data loader [ {} ].".format(load_date)
    )
    return True


def event_data_loader(*args):
    logger.warning("Start: Event data loader.")

    # Args
    load_date = args[0]

    # Check that load date is a date
    if not isinstance(load_date, datetime.date):
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
        return

    session = get_session(current_app)[1]

    tl_model = TablesLoadedModel.worker_find(session, load_date)

    if not tl_model:
        tl_model = TablesLoadedModel(loaded_date=load_date)
        session.add(tl_model)
        session.commit()

    if tl_model and tl_model.calls_loaded:
        logger.warning(
            "Event data for [ {} ] already loaded.".format(load_date)
        )
        return

    # Get the data from the source database
    ext_session = get_external_session(ext_uri)

    try:
        results = ext_session.query(EventTableModel).filter(
            func.DATE(EventTableModel.start_time) == load_date
        ).all()
    except DatabaseError:
        logger.error("Failed to get records from source database.")
    else:
        # Insert data into target database
        try:
            load_event_data(session, results)

            session.commit()
        except DatabaseError:
            logger.error("Error committing event records to target database.")
            session.rollback()

    # Update the system that the interval is loaded
    if load_date < utc_now().date():
        tl_model.events_loaded = True
    tl_model.last_updated = utc_now()
    session.add(tl_model)
    session.commit()

    logger.warning(
        "Completed event data loader [ {} ].".format(load_date)
    )
    return True


def report_loader(*args):
    logger.warning("Started: Report loader.")

    # Args
    start_time = args[0]
    end_time = args[1]

    # Check that start and end times are datetime
    if (
        not isinstance(start_time, datetime.datetime) and
        not isinstance(end_time, datetime.datetime)
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

    session = get_session(current_app)[1]

    report = SlaReportModel.worker_get(session, start_time, end_time)
    if not report:
        report = SlaReportModel(
            start_time=start_time, end_time=end_time, last_updated=utc_now()
        )
    else:
        report.last_updated = utc_now()

    # Add new report, or update last_updated
    session.add(report)
    session.commit()

    # Get the report data
    if report.data:
        logger.info(
            "Report exists for {start} to {end}.\n".format(
                start=start_time, end=end_time
            )
        )
        return

    report_data = build_sla_data(start_time, end_time)

    if not report_data:
        logger.error(
            "Error: Could not build report for: {start} and {end}.\n".format(
                start=start_time, end=end_time
            )
        )
        return

    # Finish the report and commit
    report.data = report_data
    session.add(report)
    session.commit()

    # Update the system that the report is complete
    report.last_updated = utc_now()
    report.completed_on = utc_now()
    session.add(report)
    session.commit()

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
