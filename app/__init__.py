from flask import render_template, request, g
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_restful.reqparse import RequestParser
from healthcheck import HealthCheck, EnvironmentDump
from sqlalchemy.exc import DatabaseError


from .database import init_db, get_sql_alchemy, get_session
from .util import Flask, make_celery, AlchemyEncoder, get_nav


app = Flask(
    __name__,
    instance_relative_config=True,
    instance_path='/tmp',
    template_folder='templates',
    static_folder='static',
    static_url_path='/static'
)


# Settings
app.config.from_object('app.celery_config.Config')
app.config.from_object('app.default_config.DevelopmentConfig')


# Services
mail = Mail(app)
celery = make_celery(app)
Bootstrap(app)
nav = get_nav(app)
moment = Moment(app)
health = HealthCheck(app, "/healthcheck")
envdump = EnvironmentDump(app, "/environment")
db = get_sql_alchemy(app)
init_db(db)


@app.before_first_request
def startup_setup():
    from app.util import add_cdns
    add_cdns(app)
    if not app.debug:
        app.config.from_object('app.default_config.ProductionConfig')
        from app.util import init_logging
        init_logging(app, mail)


# Set JSON serializer for the application
from app.util.tasks import serialization_register_json

serialization_register_json()


# Init task stuff
from app.data.tasks import add_scheduled_tasks as add_scheduled_data_tasks

add_scheduled_data_tasks(app)


# Modules
from .frontend import frontend_bp
from .backend import api_bp

app.register_blueprint(frontend_bp)
app.register_blueprint(api_bp)


from app.util.health_tests import get_local_healthcheck, get_data_healthcheck

health.add_check(get_local_healthcheck)
health.add_check(get_data_healthcheck)


# envdump.add_section("application", app)


# Configuration for API
@app.before_request
def before_request():
    from .util.tasks import to_datetime

    # Default parser arguments
    g.parser = RequestParser()
    g.parser.add_argument(
        'task', dest='task', help='A task to complete.'
    )

    # Session + Parser configuration
    if request.endpoint in ("backend.client", "backend.data"):
        g.local_session = get_session(app.config['SQLALCHEMY_DATABASE_URI'])
        # Client API arguments
        g.parser.add_argument(
            'client_name', dest='client_name', location='form',
            help='A client to change.'
        )
        g.parser.add_argument(
            'client_ext', dest='client_ext', location='form',
            type=int, help='The client number to change.'
        )
    if request.endpoint in ("backend.data",):
        g.ext_session = get_session(app.config['EXTERNAL_DATABASE_URI'], readonly=True)
        # Data API arguments
        g.parser.add_argument(
            'start_time', dest='start_time', type=to_datetime,
            help='Start time for data interval.'
        )
        g.parser.add_argument(
            'end_time', dest='end_time', type=to_datetime,
            help='End time for data interval.'
        )


# Commit and remove API sessions
@app.after_request
def after_request(response):
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

    return response


# Error pages
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html', title='Page Not Found'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html', title='Resource Error'), 500
