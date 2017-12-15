from flask_mail import Mail
from app.util import Flask, make_celery, AlchemyEncoder, get_logger, get_handler


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


# Logger
@app.before_first_request
def setup_logging():
    if not app.debug:
        file_handler = get_handler('tmp/app.log')
        server_logger = get_logger('werkzeug')
        server_logger.addHandler(file_handler)
        app.logger.addHandler(file_handler)


# Services
mail = Mail(app)


# Set the json encoder
app.json_encoder = AlchemyEncoder


# Init tasks
celery = make_celery(app)
from app.tasks import test


# Import views
from .view import *
