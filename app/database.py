from sqlalchemy.orm import scoped_session, sessionmaker
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base

from app.util.base_models import convention, NoNameMeta, ModelBase


def get_sql_alchemy(app):
    metadata = MetaData(naming_convention=convention)
    return SQLAlchemy(
        app, metadata=metadata,
        model_class=declarative_base(cls=ModelBase, metaclass=NoNameMeta, name='Model')
    )


def get_scoped_session(app, db, bind=None):
    return scoped_session(
        sessionmaker(autocommit=False, autoflush=False,
                     bind=db.engine if bind is None else db.get_engine(app, bind))
    )


def init_db(o):
    # Create database and tables
    from app.report.models import SLAReport
    from app.data.models import CallTable, EventTable, LocalEventTable, LocalCallTable
    o.create_all(bind=[None, 'app_meta'])
