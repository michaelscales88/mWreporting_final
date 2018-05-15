# data/services/loaders.py
import logging
import pandas as pd
from datetime import date as DATETYPE, datetime, timedelta
from flask import current_app
from sqlalchemy.sql import and_, func


from backend.services import get_session
from backend.services.app_tasks import get_model, get_pk, get_foreign_id, parse_time
from backend.factories import create_application
from backend.factories import create_celery


celery = create_celery(create_application())


def check_loaded(table_name, date):
    loader_model = get_model('tables_loaded')
    if isinstance(date, DATETYPE):
        return loader_model.check_date_set(date, table_name)
    else:
        return False


def filter_loaded(table_name, date_range):
    loader_model = get_model('tables_loaded')
    for date in date_range:
        # Coerce datetimes into dates to maintain invariant
        if isinstance(date, datetime):
            date = date.date()
            if not loader_model.check_date_set(date, table_name):
                yield date
        elif isinstance(date, DATETYPE):
            if not loader_model.check_date_set(date, table_name):
                yield date


@celery.task(name='data.tasks.data_loader')
def data_loader(periods=60, table_names=('c_call', 'c_event')):
    """
    Maintains the invariant of whole day record loads to ensure that all
    records are present for a report being run.
    Call the load_data_for_date_range fn for a date period (default 60).
    The number of periods loaded should minimize the strain on the source
    system. This process is invoked for each table_name in table_names.
    Returns True if the fn runs for the entire date_list.
    """
    if not current_app or not current_app.config.get('MAX_INTERVAL'):
        max_interval = 5
    else:
        max_interval = current_app.config['MAX_INTERVAL']
        print('found settings for MAX INTERVAL')

    # Generate dates to check: generates dt objects
    date_list = pd.date_range(pd.datetime.today() - timedelta(days=int(periods)), periods=int(periods)).tolist()
    # Manifest holds tables and the specific dates
    # which need to be loaded.
    date_manifest = {table_name: [] for table_name in table_names}
    # Prune days which are already loaded resulting
    # list has been converted from datetime to date
    # objects
    for table_name in table_names:
        for date in filter_loaded(table_name, date_list):
            date_manifest[table_name].append(date)

    for table_name, date_periods in date_manifest.items():
        # Limit the size of each query to max number of days of records
        date_periods = date_periods[:max_interval if len(date_periods) > max_interval else len(date_periods)]
        load_data_for_date_range(table_name, periods=date_periods)
    return True


@celery.task(name='data.tasks.load_data_for_date_range')
def load_data_for_date_range(table_name, start_date=None, end_date=None, periods=()):
    """
    Add data in whole day increments.
    For a table_name in the db, add records in whole day increments and update
    loaded_tables for that date.
    Returns True if data is loaded and False if no data is loaded/error occurs.
    """
    table = get_model(table_name)
    loader_model = get_model('tables_loaded')

    # Coerce json to date
    if isinstance(start_date, (str, datetime)):
        start_date = start_date.date() if isinstance(start_date, datetime) else parse_time(start_date).date()

    # Coerce datetime to date
    if isinstance(end_date, (str, datetime)):
        end_date = end_date.date() if isinstance(end_date, datetime) else parse_time(end_date).date()

    if (table is not None
            and (isinstance(start_date, DATETYPE) and isinstance(end_date, DATETYPE))
            or len(periods) > 0):
        ext_session = get_session(current_app.config['EXTERNAL_DATABASE_URI'], readonly=True)
        try:
            # Get the data from the source database
            if len(periods) > 0:
                results = ext_session.query(table).filter(
                    func.DATE(table.start_time).in_(periods)
                )
            else:
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
                record_date = record['start_time'].date()
                date_data = grouped_data.get(record_date, [])
                date_data.append(record)
                grouped_data[record_date] = date_data

            # Add the records from the external database to the local database.
            foreign_key = get_pk(table)

            # Add records by date
            for date, data in grouped_data.items():
                # Check table: loaded_tables whether records are loaded
                date_loaded = check_loaded(table_name, date)
                if not date_loaded:
                    for record in data:
                        record_exists = table.find(get_foreign_id(record, foreign_key)) is not None
                        if not record_exists:
                            # Filter out the unwanted data
                            table.create(
                                **{entry: record[entry] for entry in record if entry != '_sa_instance_state'}
                            )
                    # Update loader model with the table and date loaded
                    loader_model.create(date_loaded=date, table=table_name)

                # else:
                #     # Records already loaded
                #     print('records already loaded', table_name, date)
                #     pass

        except Exception as err:
            logging.info(err)
            logging.info("Error in data/services/loaders.py")
            ext_session.rollback()
            return False
        else:
            # Commit records and updated the table: tables_loaded
            table.session.commit()
            loader_model.session.commit()
            return True
        finally:
            # Always close the connection to the external database
            ext_session.close()
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
