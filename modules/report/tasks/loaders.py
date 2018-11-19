# data/services/loaders.py
import datetime
from json import dumps

from flask import current_app
from sqlalchemy.sql import func, or_, and_

from modules.celery_tasks import task_logger as logger
from modules.celery_worker import celery
from modules.utilities import get_pk, utc_now
from modules.report.models import (
    TablesLoadedModel, CallTableModel, EventTableModel, SlaReportModel,
    SummarySLAReportModel
)
from modules.report.utilities import get_external_session
from .report_tasks import make_summary_sla_report, make_sla_report


@celery.task(name='report.utilities.data_loader')
def data_loader(*args):
    """

    """
    logger.warning("Started: Data loader.")

    # TODO: Convert to a working query
    dates_query = None

    for report in TablesLoadedModel.all():
        if not report.complete:
            if report.last_updated:
                if report.last_updated < utc_now() - datetime.timedelta(minutes=5):
                    dates_query = report
                    break
            else:
                dates_query = report
                break

    if dates_query:
        dates_query.update(last_updated=utc_now())
        dates_query.session.commit()
    else:
        logger.info("No tables to load.")
        return "Success: No tasks."

    ext_uri = current_app.config.get('EXTERNAL_DATABASE_URI')
    if not ext_uri:
        logger.error("Error: External database connection not set.\n"
                     "Add 'EXTERNAL_DATABASE_URI' to your config with\n"
                     "the address to your database.")
        return "Error: No external connection available."

    ext_session = get_external_session(ext_uri)

    load_info = {
        CallTableModel: dates_query.loaded_date, EventTableModel: dates_query.loaded_date
    }
    try:
        for table, loaded_date in load_info.items():
            # Get the data from the source database
            results = ext_session.query(table).filter(
                func.DATE(table.start_time) == loaded_date
            )
            # Slice the data up by date to keep track of dates loaded
            grouped_data = {}
            for r in results.all():
                record = r.__dict__
                record_date = record['start_time'].date()
                dates_records = grouped_data.get(record_date, [])
                dates_records.append(record)
                grouped_data[record_date] = dates_records

            matching_key = get_pk(table)

            # Add the records from the external database to the local
            # database. Add record by record grouped by date. Check if
            # the record exists before adding.
            for date, gr in grouped_data.items():
                for rec in gr:
                    primary_key = rec.get(matching_key)
                    if not primary_key:
                        logger.error("Could not identify primary key for foreign record.\n"
                                     "{dump}".format(dump=dumps(gr, indent=2, default=str)))
                        continue

                    record = table.find(primary_key)
                    if not record:
                        table.create(
                            **{
                                entry: rec[entry]
                                for entry in rec.keys() if entry != '_sa_instance_state'
                            }
                        )
                    else:
                        logger.warning("Record Exists: {rec}".format(rec=record))

                tl_model = TablesLoadedModel.find(date)
                if table.__tablename__ == "c_call":
                    tl_model.update(calls_loaded=True)
                if table.__tablename__ == "c_event":
                    tl_model.update(events_loaded=True)
                TablesLoadedModel.session.commit()

            table.session.commit()
            table.session.close()

    except Exception as err:
        logger.error("Error: Major failure loading data.")
        return dumps(err, indent=4, default=str)
    else:
        logger.info("Success: Loaded all data for task request.")
        return "Success: Tables loaded."
    finally:
        # Always close the connection to the external database
        ext_session.close()

        logger.info("Closed external data connection.")

        logger.warning("Completed: Summary report loader.")


@celery.task(name='report.utilities.report_loader')
def report_loader(*args):
    logger.warning("Started: Report loader {}".format(utc_now()))

    # TODO: Convert to a working query
    next_report = None

    for report in SlaReportModel.all():
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