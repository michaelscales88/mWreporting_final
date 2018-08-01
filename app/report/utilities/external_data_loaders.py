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
from ..models import TablesLoadedModel

app_logger = logging.getLogger("app")
task_logger = get_task_logger(__name__)


def check_loaded(table_name, date):
    loader_model = get_model_by_tablename('tables_loaded')
    print(loader_model)
    if isinstance(date, DATETYPE):
        print(loader_model.query.filter(
            and_(
                loader_model.date_loaded == date,
                loader_model.table == table_name
            )
        ).first())
        return loader_model.check_date_set(date, table_name)
    else:
        return False


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
    TOTAL_LIMIT = current_app.config.get('MAX_INTERVAL', 10)
    dates_to_load = TablesLoadedModel.query.filter(
        TablesLoadedModel.is_loaded == False
    ).limit(
        TOTAL_LIMIT
    ).all()

    c_call_dates = [date for date in dates_to_load if date.table == 'c_call']
    app_logger.info(dumps({
        "Message": "Loading data.",
        "Date": c_call_dates,
        "Table": "c_call"
    }, indent=2, default=str))
    # load_data_for_date_range(date.table, start_date=)
    c_event_dates = [date for date in dates_to_load if date.table == 'c_event']
    app_logger.info(dumps({
        "Message": "Loading data.",
        "Date": c_event_dates,
        "Table": "c_event"
    }, indent=2, default=str))
    #
    # for table_name, date_periods in date_manifest.items():
    #     # Limit the size of each query to max number of days of records
    #     date_periods = date_periods[:max_interval if len(date_periods) > max_interval else len(date_periods)]
    #     load_data_for_date_range(table_name, periods=date_periods)
    return True


@celery.task(name='report.utilities.load_data_for_date_range')
def load_data_for_date_range(table_name, start_date=None, end_date=None, periods=(), dates=()):
    print("starting load data for range")
    """
    Add data in whole day increments.
    For a table_name in the db, add records in whole day increments and update
    loaded_tables for that date.
    Returns True if data is loaded and False if no data is loaded/error occurs.
    """
    # table = get_model_by_tablename(table_name)
    # loader_model = get_model_by_tablename('tables_loaded')
    #
    # # Coerce json to date
    # if isinstance(start_date, (str, datetime)):
    #     start_date = start_date.date() if isinstance(start_date, datetime) else parse_time(start_date).date()
    #
    # # Coerce datetime to date
    # if isinstance(end_date, (str, datetime)):
    #     end_date = end_date.date() if isinstance(end_date, datetime) else parse_time(end_date).date()
    #
    # if (table is not None
    #         and (isinstance(start_date, DATETYPE) and isinstance(end_date, DATETYPE))
    #         or len(periods) > 0):
    #     ext_session = get_external_session(current_app.config['EXTERNAL_DATABASE_URI'])
    #     try:
    #         # Get the data from the source database
    #         if len(periods) > 0:
    #             results = ext_session.query(table).filter(
    #                 func.DATE(table.start_time).in_(periods)
    #             )
    #         else:
    #             results = ext_session.query(table).filter(
    #                 and_(
    #                     table.start_time >= start_date,
    #                     table.end_time <= end_date
    #                 )
    #             )
    #
    #         # Slice the data up by date
    #         grouped_data = {}
    #         for r in results.all():
    #             # Organize records by date
    #             record = r.__dict__
    #             record_date = record['start_time'].date()
    #             date_data = grouped_data.get(record_date, [])
    #             date_data.append(record)
    #             grouped_data[record_date] = date_data
    #
    #         # Add the records from the external database to the local database.
    #         foreign_key = get_pk(table)
    #
    #         # Add records by date
    #         for date, data in grouped_data.items():
    #             # Check table: loaded_tables whether records are loaded
    #             date_loaded = check_loaded(table_name, date)
    #             if not date_loaded:
    #                 for record in data:
    #                     record_exists = table.find(get_foreign_id(record, foreign_key)) is not None
    #                     if not record_exists:
    #                         # Filter out the unwanted data
    #                         table.create(
    #                             **{entry: record[entry] for entry in record if entry != '_sa_instance_state'}
    #                         )
    #                 # Update loader model with the table and date loaded
    #                 loader_model.create(date_loaded=date, table=table_name)
    #
    #     except Exception as err:
    #         task_logger.error(err)
    #         app_logger.error("Error loading data.")
    #         ext_session.rollback()
    #         return False
    #     else:
    #         # Commit records and updated the table: tables_loaded
    #         table.session.commit()
    #         loader_model.session.commit()
    #         app_logger.info("Loaded records", table_name)
    #         return True
    #     finally:
    #         # Always close the connection to the external database
    #         ext_session.close()
    return False


@celery.task(name='data.tasks.test_load_data_for_date_range')
def test_load_data_for_date_range(table_name, start_date, end_date):
    logging.info(table_name)
    logging.info(parse_time(start_date))
    logging.info(end_date)

    # Coerce json to date
    if isinstance(start_date, (str, datetime)):
        start_date = start_date.date() if isinstance(start_date, datetime) else parse_time(start_date).date()

    # Coerce datetime to date
    if isinstance(end_date, (str, datetime)):
        end_date = end_date.date() if isinstance(end_date, datetime) else parse_time(end_date).date()
    print('start_date', start_date)
    print('end_date', end_date)
    return True
