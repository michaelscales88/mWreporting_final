# data/services/loaders.py
import datetime

from flask import current_app
from json import dumps
from sqlalchemy.sql import func

from modules.celery_tasks import task_logger as logger
from modules.celery_worker import celery
from modules.core import get_pk, utc_now
from modules.report.models import TablesLoadedModel, CallTableModel, EventTableModel
from .helpers import get_external_session


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
            table.session.remove()

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
