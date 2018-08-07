# data/services/loaders.py
import logging
from json import dumps
from datetime import date as DATETYPE, datetime, timedelta
from flask import current_app
from sqlalchemy.sql import and_, func
from celery.utils.log import get_task_logger

from .external_data_helpers import get_external_session
from app.utilities.helpers import get_model_by_tablename, get_pk, get_foreign_id, parse_time
from app.celery import celery, SqlAlchemyTask

app_logger = logging.getLogger("app")
task_logger = get_task_logger(__name__)


def filter_loaded(table_name, date_range):
    loader_model = get_model_by_tablename('tables_loaded')
    for date in date_range:
        # Coerce datetimes into dates to maintain invariant
        if isinstance(date, datetime):
            date = date.date()
            if not loader_model.check_date_set(date, table_name):
                yield date
        elif isinstance(date, DATETYPE):
            if not loader_model.check_date_set(date, table_name):
                yield date


@celery.task(base=SqlAlchemyTask, name='report.utilities.data_loader')
def data_loader(*args):
    """

    """
    tables_loaded = get_model_by_tablename("loaded_tables")
    dates_to_load = tables_loaded.query.filter(
        and_(
            tables_loaded.is_loaded.is_(False),
            tables_loaded.date_downloaded.is_(None)
        )
    ).limit(
        current_app.config.get('MAX_INTERVAL', 10)
    ).all()

    for date in dates_to_load:
        date.update(date_downloaded=datetime.utcnow())
    tables_loaded.session.commit()

    if not len(dates_to_load) > 0:
        task_logger.info("No tables to load.")
        return "Success: No tasks."

    c_call_dates = [date for date in dates_to_load if date.table == 'c_call']
    if c_call_dates:
        app_logger.info(dumps({
            "Message": "Loading data.",
            "Date": c_call_dates,
            "Table": "c_call"
        }, indent=2, default=str))
        status = load_date_models(date_models=c_call_dates)
        # TODO: add granularity to error reporting/logging
        if status == "error":
            return "Error"

    c_event_dates = [date for date in dates_to_load if date.table == 'c_event']
    if c_event_dates:
        app_logger.info(dumps({
            "Message": "Loading data.",
            "Date": c_event_dates,
            "Table": "c_event"
        }, indent=2, default=str))
        status = load_date_models(date_models=c_event_dates)
        if status == "error":
            return "Error"

    return "Success: Tables loaded."


@celery.task(name='report.utilities.load_data_for_date_range')
def load_data_for_date_range(self, table_name=None, start_date=None, end_date=None):
    """
    Add data in whole day increments.
    For a table_name in the db, add records in whole day increments and update
    loaded_tables for that date.

    Modes:
    - start_date/end_date: iterates from the start date up to the end date
    Returns True if data is loaded and False if no data is loaded/error occurs.
    """
    table = get_model_by_tablename(table_name)
    if not table:
        print("returning on no model")
        return "error"

    print("getting loader model")
    loader_model = get_model_by_tablename('loaded_tables')

    print("checking date interval configuration")
    if start_date and end_date:
        # Coerce json to date
        if isinstance(start_date, (str, datetime)):
            start_date = start_date.date() if isinstance(
                start_date, datetime
            ) else parse_time(start_date).date()

        # Coerce datetime to date
        if isinstance(end_date, (str, datetime)):
            end_date = end_date.date() if isinstance(
                end_date, datetime
            ) else parse_time(end_date).date()

        task_logger.info(
            "Loading data for request: {start_date} to {end_date}.".format(
                start_date=start_date, end_date=end_date
            )
        )
    else:
        task_logger.error(
            "Bad request: no dates or date range."
        )

    print("passed logger stuff")
    if start_date and end_date:
        ext_session = get_external_session(current_app.config['EXTERNAL_DATABASE_URI'])
        try:
            # Get the data from the source database
            results = ext_session.query(table).filter(
                and_(
                    table.start_time >= start_date,
                    table.end_time <= end_date
                )
            )

            # Slice the data up by date
            grouped_data = {}
            for r in results.all():
                # Organize records by date
                record = r.__dict__
                print(record)
                record_date = record['start_time'].date()
                date_data = grouped_data.get(record_date, [])
                date_data.append(record)
                grouped_data[record_date] = date_data

            # Add the records from the external database to the local database.
            foreign_key = get_pk(table)

            # Add records by date
            # for date, data in grouped_data.items():
            #     # Check table: loaded_tables whether records are loaded
            #     date_loaded_model = loader_model.find_table_by_date(date, table)
            #     if not date_loaded_model:
            #         # Update loaded_tables with the table and date loaded
            #         date_loaded_model = loader_model.create(loaded_date=date, table=table_name)
            #
            #     if not date_loaded_model.is_loaded:
            #         print("loading records")
            #         for record in data:
            #             record_exists = table.find(get_foreign_id(record, foreign_key)) is not None
            #             if not record_exists:
            #                 # Filter out the unwanted data
            #                 table.create(
            #                     **{
            #                         entry: record[entry]
            #                         for entry in record if entry != '_sa_instance_state'
            #                     }
            #                 )
            #         date_loaded_model.update(is_loaded=True)
            #         app_logger.info(
            #             "Loaded [ {table} ] records for {date}.".format(
            #                 table=table_name,
            #                 date=date
            #             )
            #         )

        except Exception as err:
            task_logger.error(err)
            app_logger.error("Error loading data.")
            ext_session.rollback()
            return "error"
        else:
            # Commit records and updated the table: tables_loaded
            table.session.commit()
            loader_model.session.commit()
            task_logger.info("Success: Loaded all data for task request.")
            return True
        finally:
            # Always close the connection to the external database
            ext_session.close()
            task_logger.info("Closed external data connection.")

    return "error"


def load_date_models(date_models=()):
    """
    Add data in whole day increments.
    For a table_name in the db, add records in whole day increments and update
    loaded_tables for that date.

    Returns True if data is loaded and False if no data is loaded/error occurs.
    """
    table = get_model_by_tablename(date_models[0].table)
    if date_models:
        task_logger.info(
            "Loading data for dates request: {dates}.".format(
                dates=dumps(date_models, indent=2, default=str)
            )
        )
    else:
        task_logger.error(
            "Bad request: no dates or date range."
        )

    if len(date_models) > 0:
        ext_session = get_external_session(current_app.config['EXTERNAL_DATABASE_URI'])
        try:
            dates = [model.loaded_date for model in date_models]

            # Get the data from the source database
            results = ext_session.query(table).filter(
                func.DATE(table.start_time).in_(dates)
            )

            # Slice the data up by date
            grouped_data = {}
            for r in results.all():
                # Organize records by date
                record = r.__dict__
                record_date = record['start_time'].date()
                date_data = grouped_data.get(record_date, [])
                date_data.append(record)
                grouped_data[record_date] = date_data

            # Add the records from the external database to the local database.
            foreign_key = get_pk(table)

            # Add records by date
            # TODO: convert this to map
            for date_model in date_models:
                if date_model.is_loaded is False:
                    data = grouped_data.get(date_model.loaded_date)
                    if data:
                        for data_rec in data:
                            record_exists = table.find(get_foreign_id(data_rec, foreign_key)) is not None
                            if not record_exists:
                                # Filter out the unwanted data
                                table.create(
                                    **{
                                        entry: data_rec[entry]
                                        for entry in data_rec if entry != '_sa_instance_state'
                                    }
                                )
                        date_model.update(is_loaded=True)
                        app_logger.info(
                            "Loaded [ {table} ] records for {date}.".format(
                                table=date_model.table,
                                date=date_model.loaded_date
                            )
                        )
                    else:
                        # Put the task back in the pool
                        date_model.update(date_downloaded=None)
                        app_logger.warning(
                            "Failed to load [ {table} ] records for {date}.".format(
                                table=date_model.table,
                                date=date_model.loaded_date
                            )
                        )
                    date_model.session.commit()

        except Exception as err:
            task_logger.error(err)
            app_logger.error("Error loading data.")
            ext_session.rollback()
            table.session.rollback()
            raise err
        else:
            task_logger.info("Success: Loaded all data for task request.")
            return True
        finally:
            # Always close the connection to the external database
            ext_session.close()
            task_logger.info("Closed external data connection.")

    return "error"


