# data/services/loaders.py
import logging
import pandas as pd
from datetime import date as DATETYPE, datetime
from flask import current_app
from sqlalchemy.sql import and_

from backend import celery
from backend.services import get_session
from backend.services.app_tasks import get_model, get_pk, get_foreign_id, parse_time


def check_loaded(date, table_name):
    loader_model = get_model('tables_loaded')
    if isinstance(date, DATETYPE):
        return loader_model.check_date_set(date, table_name)
    else:
        return False


@celery.task()
def data_loader(periods=60):
    datelist = pd.date_range(pd.datetime.today().date(), periods=int(periods)).tolist()
    for date in datelist:
        print(type(date), date)
    return True


@celery.task()
def load_data_for_date_range(table_name, start_date, end_date):
    """
    Add data in whole day increments.
    For a table_name in the db, add records in whole day increments and update
    loaded_tables for that date.
    """
    table = get_model(table_name)
    loader_model = get_model('tables_loaded')

    # Coerce json to date
    if isinstance(start_date, (str, datetime)):
        start_date = start_date.date() if isinstance(start_date, datetime) else parse_time(start_date).date()

    # Coerce datetime to date
    if isinstance(end_date, (str, datetime)):
        end_date = end_date.date() if isinstance(end_date, datetime) else parse_time(end_date).date()

    if isinstance(start_date, DATETYPE) and isinstance(end_date, DATETYPE) and table is not None:
        ext_session = get_session(current_app.config['EXTERNAL_DATABASE_URI'], readonly=True)
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
                record_date = record['start_time'].date()
                date_data = grouped_data.get(record_date, [])
                date_data.append(record)
                grouped_data[record_date] = date_data

            # Add the records from the external database to the local database.
            foreign_key = get_pk(table)

            # Add records by date
            for date, data in grouped_data.items():
                # Check table: loaded_tables whether records are loaded
                date_loaded = check_loaded(date, table_name)
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
        else:
            # Commit records and updated the table: tables_loaded
            table.session.commit()
            loader_model.session.commit()
        finally:
            # Always close the connection to the external database
            ext_session.close()
        return True
    return False


@celery.task()
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
