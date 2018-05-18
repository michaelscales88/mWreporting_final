# services/extensions.py
from flask_assets import Environment
from flask_babel import Babel
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_marshmallow import Marshmallow
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from healthcheck import HealthCheck

from . import BaseModel, get_nav


# Services
babel = Babel()
db = SQLAlchemy(model_class=BaseModel)  # Database manager
mail = Mail()                           # Mailer
bootstrap = Bootstrap()                 # Styles
nav = get_nav()                         # Navigation Bar
moment = Moment()                       # MomentJS
health = HealthCheck()                  # Resource information
ma = Marshmallow()                      # Serialization Schema
assets = Environment()                  # Static JS bundling and minification

