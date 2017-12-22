from app import app, db


from app.database import get_scoped_session


def health_database_status(db_session, session_name):
    is_database_working = True
    output = 'database: {session} is ok'.format(session=session_name)

    try:
        # to check database we will execute raw query
        db_session.execute('SELECT 1')
    except Exception as e:
        output = str(e)
        is_database_working = False
    finally:
        db_session.remove()

    return is_database_working, output


def get_local_healthcheck():
    return health_database_status(get_scoped_session(app, db, bind=None), 'local')


def get_data_healthcheck():
    return health_database_status(get_scoped_session(app, db, bind='ext_data'), 'data')


def get_app_healthcheck():
    return health_database_status(get_scoped_session(app, db, bind='app_meta'), 'app')
