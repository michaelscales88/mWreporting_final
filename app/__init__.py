from __future__ import absolute_import
from app.util import Flask, make_celery, AlchemyEncoder


# store private information in instance
app = Flask(
    __name__,
    instance_relative_config=True,
    instance_path='/var/www/tmp/',
    template_folder='templates',
    static_folder='static',
    static_url_path='/static'
)


# Set the json encoder
app.json_encoder = AlchemyEncoder


# Init task queue
celery = make_celery(app)
