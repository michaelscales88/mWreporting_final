# backend/server.py
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from healthcheck import HealthCheck


from .services import make_celery, get_nav, AppJSONEncoder, migration_meta, BaseModel


server = Flask(
    __name__,
    instance_relative_config=True,
    # instance_path='/instance',
    template_folder='../static/templates',
    static_folder='../static'
)

# Set JSON serializer for the application
server.json_encoder = AppJSONEncoder


# Settings - cfg settings override environment and default
server.config.from_object('backend.celery_config.Config')
server.config.from_object('backend.default_config.DevelopmentConfig')
server.config.from_pyfile('app.cfg', silent=False)


# Database manager
db = SQLAlchemy(
    server,
    # metadata=migration_meta(),
    model_class=BaseModel
)


def init_db():
    # Create database and tables
    # Must import Models before calling create_all to ensure
    # tables and metadata are created

    from backend.client.models import ClientModel
    from backend.data.models import EventTableModel, CallTableModel, TablesLoaded
    from backend.report.models import SlaReportModel

    db.create_all()


def bind_model_session():
    # Inject session to be used by Models
    BaseModel.set_session(db.session)


# Services
mail = Mail(server)
celery = make_celery(server)
Bootstrap(server)
nav = get_nav()
nav.init_app(server)
moment = Moment(server)
health = HealthCheck(server, "/healthcheck")


@celery.task
def send_async_email(msg):
    """Background task to send an email with Flask-Mail."""
    mail.send(msg)
