# util/app_handlers
from flask import render_template, request, g
from flask_restful.reqparse import RequestParser
from sqlalchemy.exc import DatabaseError

from app import app, mail
from app.database import get_session


# Configuration for APP
@app.before_first_request
def startup_setup():
    if not app.debug:
        app.config.from_object('app.default_config.ProductionConfig')
        from app.util import init_logging
        init_logging(app, mail)


# Configuration for API
@app.before_request
def before_request():
    from .tasks import to_datetime

    # Default parser arguments
    g.parser = RequestParser()
    g.parser.add_argument(
        'task', dest='task', help='A task to complete.'
    )

    # Parser configuration
    if request.endpoint in ("backend.client",):
        # Client API arguments
        g.parser.add_argument(
            'client_name', dest='client_name', location='form',
            help='A client to change.'
        )
        g.parser.add_argument(
            'client_ext', dest='client_ext', location='form',
            type=int, help='The client number to change.'
        )
    elif request.endpoint in ("backend.report",  "backend.data"):
        # Data API arguments
        g.parser.add_argument(
            'start_time', dest='start_time', type=to_datetime,
            help='Start time for data interval.'
        )
        g.parser.add_argument(
            'end_time', dest='end_time', type=to_datetime,
            help='End time for data interval.'
        )
    else:
        pass

    # Session configuration
    if request.endpoint in ("backend.report", "backend.client", "backend.data"):
        g.local_session = get_session(app.config['SQLALCHEMY_DATABASE_URI'])

    if request.endpoint in ("backend.data",):
        g.ext_session = get_session(app.config['EXTERNAL_DATABASE_URI'], readonly=True)


def commit_sessions():
    """
    Manage committing local sessions. Will remove the read-only
    External Session only if one exists for this request
    :return:
    """
    ext_session = g.get('ext_session')
    if ext_session:
        ext_session.remove()
        print('remove_session external', ext_session)

    session = g.get('local_session')
    if session:
        try:
            print('trying to commit internal session')
            session.commit()
            print('commit session internal: ', session)
        # Rollback a bad session
        except DatabaseError as e:
            print('Rolling back internal session', e)
            session.rollback()
        # Always close the session
        finally:
            print('remove session internal: ', session)
            session.remove()


def rollback_sessions():
    """
    Prevent committing any session changes
    :return:
    """
    session = g.get('local_session')
    if session:
        # Prevent after_request handler from committing data if aborting
        session.rollback()


# Commit and remove API sessions
@app.after_request
def after_request(response):
    commit_sessions()
    return response


# Error pages
@app.errorhandler(404)
def not_found_error(error):
    rollback_sessions()
    return render_template('404.html', title='Page Not Found'), 404


@app.errorhandler(500)
def internal_error(error):
    rollback_sessions()
    return render_template('500.html', title='Resource Error'), 500
