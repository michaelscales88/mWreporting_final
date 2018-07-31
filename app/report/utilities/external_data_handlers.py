# data/services/data.py
from sqlalchemy.sql import and_
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.utilities import get_model, query_to_frame


def get_data_for_table(table_name, start_time, end_time):
    table = get_model(table_name)
    return table.query.filter(
        and_(
            table.start_time >= start_time,
            table.end_time <= end_time
        )
    )


def get_data(table_name, start_time, end_time):
    return query_to_frame(get_data_for_table(table_name, start_time, end_time))


def abort_ro(*args,**kwargs):
    """
    Avoid writing to ro session
    """
    print("Writing operations disabled. Aborting session flush.")
    return


def get_session(engine, echo=False, readonly=False):
    engine = create_engine(engine, echo=echo)
    session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    if readonly:
        session.flush = abort_ro  # Disable flushing to db
    return session()
