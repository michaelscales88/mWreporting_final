# app/extensions.py
from flask_assets import Environment
from flask_babel import Babel
from flask_bootstrap import Bootstrap
from flask_debugtoolbar import DebugToolbarExtension
from flask_mail import Mail
from flask_marshmallow import Marshmallow
from flask_moment import Moment

from .cdn_registration import register_app_cdn
from .custom_admin import CustomAdmin

# Services
admin = CustomAdmin(template_mode='bootstrap3', base_template="admin_layout.html")
babel = Babel()
mail = Mail()                           # Mailer
bootstrap = Bootstrap()                 # Styles
moment = Moment()                       # MomentJS
serializer = Marshmallow()              # Serialization Schema
assets = Environment()                  # Static JS bundling and minification
debugger = DebugToolbarExtension()
