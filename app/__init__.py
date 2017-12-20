from flask import render_template, url_for, redirect
from flask_mail import Mail
from flask_moment import Moment
from flask_bootstrap import Bootstrap
from flask_restful import Api
from healthcheck import HealthCheck, EnvironmentDump


from app.util import Flask, make_celery, AlchemyEncoder, get_nav, get_sqlalchemy


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
db = get_sqlalchemy(app)
health = HealthCheck(app, "/healthcheck")
envdump = EnvironmentDump(app, "/environment")


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
from .home import home_blueprint
from .data import DataApi
from .report import report_blueprint, ReportApi

app.register_blueprint(home_blueprint)
app.register_blueprint(report_blueprint)

api.add_resource(DataApi, '/dataapi')
api.add_resource(ReportApi, '/reportapi')


from app.util.health_tests import get_local_healthcheck, get_app_healthcheck, get_data_healthcheck
health.add_check(get_local_healthcheck)
health.add_check(get_app_healthcheck)
health.add_check(get_data_healthcheck)
# envdump.add_section("application", app)


# Routes
@app.route('/', methods=['GET', 'POST'])
def index():
    """Render homepage"""
    return redirect(url_for('home.serve_pages'))


# Error pages
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html', title='Page Not Found'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html', title='Resource Error'), 500


if app.debug:
    print(app.url_map)
