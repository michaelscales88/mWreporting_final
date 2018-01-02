from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from healthcheck import HealthCheck, EnvironmentDump


from .database import init_db, get_sql_alchemy
from .util import Flask, make_celery, AlchemyEncoder, get_nav, add_cdns


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
db = get_sql_alchemy(app)
health = HealthCheck(app, "/healthcheck")
# envdump = EnvironmentDump(app, "/environment")
# envdump.add_section("application", app)

# Initialize db and CDNS URI
init_db(db)
add_cdns(app)


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


# Session configuration, app handling, before/after request
from app.util import app_handlers
