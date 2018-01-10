from flask_sqlalchemy import SQLAlchemy
from redpanda.orm import sessionmaker
from sqlalchemy import MetaData, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session

from app.util.base_models import convention, NoNameMeta, ModelBase


def init_db(db):
    # Create database and tables
    # Must import Models before calling create_all to ensure
    # tables and metadata are created

    from app.client.models import Client
    from app.data.models import EventTable, CallTable
    from app.report.models import SlaData

    db.create_all()


def get_sql_alchemy(app):
    metadata = MetaData(naming_convention=convention)

    db = SQLAlchemy(
        app, metadata=metadata,
        model_class=declarative_base(cls=ModelBase, metaclass=NoNameMeta, name='Model')
    )
    return db


def abort_ro(*args,**kwargs):
    """
    Avoid writing to ro session
    """
    print("Writing operations disabled. Aborting session flush.")
    return


def get_session(engine, echo=False, readonly=False):
    engine = create_engine(engine, echo=echo)
    session = scoped_session(sessionmaker(bind=engine, autoflush=False, autocommit=False))
    if readonly:
        session.flush = abort_ro  # Disable flushing to db
    return session

