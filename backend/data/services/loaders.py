# data/services/loaders.py
from datetime import date as DATETYPE, datetime
from flask import current_app
from json import dumps, loads
from sqlalchemy.sql import and_


from backend.services import get_session
from backend.services.app_tasks import get_model, get_pk, get_foreign_id


def set_loaded(table_name, date):
    loader_model = get_model('tables_loaded')
    if isinstance(date, DATETYPE):
        # Do nothing if date is set
        return loader_model.check_date_set(date, table_name)
    else:
        # Set the date as loaded
        loader_model.create(date_loaded=date, table=table_name)
        return True


def check_loaded(date, table_name):
    loader_model = get_model('tables_loaded')
    if isinstance(date, DATETYPE):
        return loader_model.check_date_set(date, table_name)
    else:
        return False


def load_data_for_date_range(table_name, start_date, end_date):
    """
    Add data in whole day increments.
    For a table_name in the db, add records in whole day increments and update
    loaded_tables for that date.
    """
    table = get_model(table_name)

    # Coerce json to date
    if isinstance(start_date, (str, datetime)):
        start_date = start_date.date() if isinstance(start_date, datetime) else loads(start_date)

    # Coerce datetime to date
    if isinstance(end_date, (str, datetime)):
        end_date = end_date.date() if isinstance(end_date, datetime) else loads(end_date)

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

            # Add records and update loaded data table
            for date, data in grouped_data.items():
                print(date)
                date_loaded = check_loaded(date, table_name)
                print('date_loaded', date_loaded)
                if not date_loaded:
                    for record in data:
                        record_exists = table.find(get_foreign_id(record, foreign_key)) is not None
                        print(record_exists)
                        if not record_exists:
                            # Filter out the unwanted data
                            print("creating record")
                            table.create(
                                **{entry: record[entry] for entry in record if entry != '_sa_instance_state'}
                            )
                    print("setting loaded")
                    # Update loaded_tables for the date
                    # TODO: move this to the point after the records are actually committed
                    set_loaded(table_name, date)
                else:
                    print("already loaded")

            print('finished adding records')
        except Exception as e:
            print('Exceptional', e)
            ext_session.rollback()
        finally:
            # Always close the connection to the external database
            ext_session.close()
        return True
