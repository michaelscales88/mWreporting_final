from redpanda.orm import sessionmaker
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import scoped_session

from app.util.db_manager import DbManager
from app import app, db


def get_scoped_session(o):
    if isinstance(o, Engine):
        return scoped_session(
            sessionmaker(autocommit=False, autoflush=False, bind=o)
        )
    else:
        print('No bind provided.')


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
    print('setting read only transaction')
    conn.execute('SET TRANSACTION READ ONLY')


print('trying to create bind for')
print(db.get_engine(app, None))
print(db.get_engine(app, 'app_meta'))

# Create database and tables
db.create_all(bind=[None, 'app_meta'])
