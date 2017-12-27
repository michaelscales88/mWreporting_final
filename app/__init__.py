from flask import render_template, request, g
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_restful import Api
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
api = Api(app)

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

app.register_blueprint(frontend_bp)

from .client.api import ClientApi
from .data.api import DataApi
from .report.api import ReportApi

api.add_resource(ClientApi, '/clientapi')
api.add_resource(DataApi, '/dataapi')
api.add_resource(ReportApi, '/reportapi')

from app.util.health_tests import get_local_healthcheck, get_data_healthcheck

health.add_check(get_local_healthcheck)
health.add_check(get_data_healthcheck)


# envdump.add_section("application", app)


# Set API sessions
@app.before_request
def before_request():
    if request.endpoint in ("clientapi",):
        g.local_session = get_session(app.config['SQLALCHEMY_DATABASE_URI'])
    else:
        pass


# Commit and remove API sessions
@app.after_request
def after_request(response):
    session = g.get('local_session')
    if session:
        try:
            session.commit()
            print('commit local session')
        # Rollback a bad session
        except DatabaseError:
            session.rollback()
        # Always close the session
        finally:
            print('remove local session')
            session.remove()
    return response


# Error pages
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html', title='Page Not Found'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html', title='Resource Error'), 500

if app.debug:
    print(app.url_map)
