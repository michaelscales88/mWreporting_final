# app/__init__.py
from flask import Flask
from flask_assets import Bundle

import frontend  # Templates directory functions as a frontend
from .base.base_model import BaseModel
from .database import get_session, init_db
from .extensions import (
    admin, bootstrap, mail, moment, babel,
    serializer, assets, debugger, register_app_cdn,
)
from .utilities.registration import register_with_app

""" Create the app """
app = Flask(
    __name__,
    template_folder='../frontend',
    static_folder="../static",
)

# Configure app settings
import modules.utilities.config_runner

# DB
engine, session = get_session(app)
# Set the session before importing FlaskAdmin views
BaseModel.set_session(session)

""" App Security + Settings """
import modules.core

""" Sub module Imports """
import modules.report
import modules.worker     # Create tasks from other subs

# Create the tables once all models have been imported
init_db(app, engine, session)

""" Init + Bind extensions to app """
# Enable/Disable development extensions
if app.debug:
    debugger.init_app(app)

admin.init_app(app)
babel.init_app(app)
bootstrap.init_app(app)
serializer.init_app(app)
mail.init_app(app)
moment.init_app(app)
assets.init_app(app)                # Manage JavaScript bundles

""" Register HTML """
# Register external CDNs
register_app_cdn(app)

# Add server's static files to be bundled and minified
js = Bundle(
    'js/selectBox.js',
    'js/tableDiv.js',
    'js/dtSelector.js',
    filters='jsmin', output='gen/packed.js'
)
css = Bundle(
    'css/style.css',
    filters='cssmin', output='gen/all.css'
)
assets.register('js_all', js)
assets.register('css_all', css)

# Nav Settings
nav = frontend.get_nav()
nav.init_app(app)
frontend.register_nav_renderers(app)

# Register HTML endpoints
app.register_blueprint(frontend.frontend_bp)
