import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import scoped_session
from redpanda.orm import sessionmaker

from app import app
from app.util.db_manager import DbManager
from .models import Base

# Internal db
if os.path.exists(app.config['SQLALCHEMY_DATABASE_URI']):
    manager = DbManager()
    manager.config_from_object(app.config)
    manager.base = Base
    manager.create()

app_db_engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=app_db_engine))

ext_pg_engine = create_engine(app.config['EXT_DATA_PG_URI'])
pg_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=ext_pg_engine))

int_pg_engine = create_engine(app.config['INT_DATA_PG_URI'])
mypg_session = scoped_session(sessionmaker(autocommit=False,
                                           autoflush=False,
                                           bind=int_pg_engine))

# Bind session to the ORM model query method
Base.query = db_session.query_property()


def init_base():
    # Import models to include in the Base
    from app.data.models import CallTable, EventTable
    from app.report.models import SLAReport
    Base.metadata.create_all(bind=app_db_engine)


@event.listens_for(ext_pg_engine, 'begin')
def receive_begin(conn):
    conn.execute('SET TRANSACTION READ ONLY')


# Create metadata during app init
init_base()
