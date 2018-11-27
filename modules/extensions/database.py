from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from modules.base_model import BaseModel


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

    BaseModel.query = session.query_property()

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        if exception:
            session.rollback()
        session.remove()

    BaseModel.metadata.create_all(bind=engine)
