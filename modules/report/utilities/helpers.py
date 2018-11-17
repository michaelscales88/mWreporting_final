# data/services/data.py
from sqlalchemy.sql import and_
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from modules.core import get_model_by_tablename


def get_data_for_table(table_name, start_time, end_time):
    table = get_model_by_tablename(table_name)
    return table.query.filter(
        and_(
            table.start_time >= start_time,
            table.end_time <= end_time
        )
    )


def abort_ro(*args, **kwargs):
    """
    Avoid writing to ro session
    """
    return


def get_external_session(engine, echo=False, readonly=True):
    engine = create_engine(engine, echo=echo)
    session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    if readonly:
        session.flush = abort_ro  # Disable flushing to db
    return session()
