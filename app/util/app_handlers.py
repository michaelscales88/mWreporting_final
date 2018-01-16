# util/app_handlers
from flask import render_template, g
from flask_restful.reqparse import RequestParser
from sqlalchemy.exc import DatabaseError

from app import app, mail


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
    # Default parser arguments
    g.parser = RequestParser()
    g.parser.add_argument(
        'task', help='A task to complete.'
    )


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
