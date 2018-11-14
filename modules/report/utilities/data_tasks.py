# data/services/loaders.py
from json import dumps
from datetime import datetime, timedelta
from flask import current_app
from sqlalchemy.sql import func, or_

from .data_helpers import get_external_session
from modules.core import get_pk
from modules.celery_worker import celery
from modules.celery_tasks import task_logger as logger
from ..models import TablesLoadedModel, CallTableModel, EventTableModel


@celery.task(name='report.utilities.data_loader')
def data_loader(*args):
    """

    """
    logger.warning("Started: Data loader.")
    # Get dates that aren't fully loaded
    dates_query = TablesLoadedModel.query.filter(
        or_(
            TablesLoadedModel.calls_loaded.is_(False),
            TablesLoadedModel.events_loaded.is_(False),
            TablesLoadedModel.complete == False
        )
    )
    # Filter to fresh dates or dates with grace time to prevent
    # multiple loads for the same date
    dates_query = dates_query.filter(
        or_(
            TablesLoadedModel.last_updated.is_(None),
            TablesLoadedModel.last_updated + timedelta(minutes=2) < datetime.now()
        )
    )
    # Minimize stressing the system by preventing massive queries
    dates_to_load = dates_query.limit(
        current_app.config.get('MAX_INTERVAL', 3)
    ).all()

    for tl_model in dates_to_load:
        tl_model.update(last_updated=datetime.utcnow().replace(microsecond=0))
    TablesLoadedModel.session.commit()

    if not len(dates_to_load) > 0:
        logger.info("No tables to load.")
        return "Success: No tasks."

    logger.info(dumps({
        "Message": "Loading data.",
        "Load Interval": ", ".join([str(tl_model.loaded_date) for tl_model in dates_to_load])
    }, indent=2, default=str))

    # Check if events and calls are needed for that date
    calls_interval = [
        tl_model.loaded_date
        for tl_model in dates_to_load if tl_model.calls_loaded == False
    ]
    call_events_interval = [
        tl_model.loaded_date
        for tl_model in dates_to_load if tl_model.events_loaded == False
    ]

    ext_uri = current_app.config.get('EXTERNAL_DATABASE_URI')
    if not ext_uri:
        logger.error("Error: External database connection not set.\n"
                     "Add 'EXTERNAL_DATABASE_URI' to your config with\n"
                     "the address to your database.")
        return "Error: No external connection available."

    ext_session = get_external_session(ext_uri)

    load_info = {
        CallTableModel: calls_interval, EventTableModel: call_events_interval
    }
    try:
        for table, loading_interval in load_info.items():
            # Get the data from the source database
            results = ext_session.query(table).filter(
                func.DATE(table.start_time).in_(loading_interval)
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

    except Exception as err:
        logger.error("Error: Major failure loading data.")
        return dumps(err, indent=4, default=str)
    else:
        logger.info("Success: Loaded all data for task request.")
        return "Success: Tables loaded."
    finally:
        # Always close the connection to the external database
        CallTableModel.session.remove()
        ext_session.close()
        logger.info("Closed external data connection.")

        logger.warning("Completed: Summary report loader.")


@celery.task(name='report.utilities.data_scheduler')
def data_scheduler(*args):
    """
    Add days to load to the system.
    :param args:
    :return:
    """
    logger.warning("Started: Data scheduler.")
    end = datetime.today().date()
    start = end - timedelta(days=40)
    for date in TablesLoadedModel.not_loaded_when2when(start, end):
        TablesLoadedModel.create(loaded_date=date)
    TablesLoadedModel.session.commit()
    logger.warning("Completed: Data scheduler.")
