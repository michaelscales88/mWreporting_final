from __future__ import absolute_import

from app.util import Flask, make_celery, AlchemyEncoder


app = Flask(
    __name__,
    instance_relative_config=True,
    instance_path='/var/www/tmp/',
    template_folder='templates',
    static_folder='static',
    static_url_path='/static'
)

# Settings
app.config.from_object('app.celeryconfig.Config')
app.config.from_object('app.default_config.DevelopmentConfig')

# Set the json encoder
app.json_encoder = AlchemyEncoder


# Init task queue
celery = make_celery(app)

from .view import *
