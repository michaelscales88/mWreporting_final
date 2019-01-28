import logging

from sqlalchemy import create_engine
from sqlalchemy.event import listens_for
from sqlalchemy.orm import scoped_session, sessionmaker

from modules.base.base_model import BaseModel

logger = logging.getLogger("app.sqlalchemy")


def get_session(app):
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], convert_unicode=True)
    return engine, scoped_session(
        sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine
        )
    )


def init_db(app, engine, session):
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        if exception:
            session.rollback()
        session.remove()

    BaseModel.metadata.create_all(bind=engine)


@listens_for(BaseModel, "after_insert", propagate=True)
def after_insert_listener(mapper, connection, target):
    if "Worker" not in str(mapper):
        warn_msg = "Inserted Record: {}".format(target)
        logger.warning(warn_msg)


@listens_for(BaseModel, "after_update", propagate=True)
def after_update_listener(mapper, connection, target):
    if "Worker" not in str(mapper):
        warn_msg = "Updated Record: {}".format(target)
        logger.warning(warn_msg)


@listens_for(BaseModel, "after_delete", propagate=True)
def after_delete_listener(mapper, connection, target):
    if "Worker" not in str(mapper):
        warn_msg = "Deleted Record: {}".format(target)
        logger.warning(warn_msg)
