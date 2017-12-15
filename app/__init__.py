from flask_mail import Mail
from app.util import Flask, make_celery, AlchemyEncoder


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
# app.config.from_object('app.default_config.ProductionConfig')


# Services
mail = Mail(app)
celery = make_celery(app)


@app.before_first_request
def startup_setup():
    if not app.debug:
        from app.util import init_logging
        init_logging(app, mail)


# Set the json encoder
app.json_encoder = AlchemyEncoder


# Celery tasks
from app.tasks import test


# Main views
from .view import *


# Modules

