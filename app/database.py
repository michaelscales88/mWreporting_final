from redpanda.orm import sessionmaker
from sqlalchemy import event
from sqlalchemy.orm import scoped_session

from app.util.db_manager import DbManager
from app import app, db


local_session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=db.engine)
)
app_session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=db.get_engine(app, 'app_meta'))
)
data_session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=db.get_engine(app, 'ext_data'))
)


@event.listens_for(db.get_engine(app, 'ext_data'), 'begin')
def receive_begin(conn):
    print('setting read only transaction', flush=True)
    conn.execute('SET TRANSACTION READ ONLY')


def init_db():
    # Create database and tables
    from app.report.models import SLAReport
    from app.data.models import CallTable, EventTable
    db.create_all(bind=[None, 'app_meta'])


init_db()
