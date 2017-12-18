from flask import render_template, url_for, redirect
from flask_mail import Mail
from flask_moment import Moment
from flask_bootstrap import Bootstrap
from flask_restful import Api

from app.util import Flask, make_celery, AlchemyEncoder, get_nav


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


@app.before_first_request
def startup_setup():
    from app.util import add_cdns
    add_cdns(app)
    if not app.debug:
        app.config.from_object('app.default_config.ProductionConfig')
        from app.util import init_logging
        init_logging(app, mail)


# Set the json encoder
# app.json_encoder = AlchemyEncoder

# Tasks sync and async
from app.util.tasks import test, serialization_register_json

# Set JSON serializer for the application
serialization_register_json()

# Modules
from .home import home_blueprint
from .report import report_blueprint, ReportApi

app.register_blueprint(home_blueprint)
app.register_blueprint(report_blueprint)

api.add_resource(ReportApi, '/report_api')


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
