# app/__init__.py
from flask import Flask
from flask_assets import Bundle

import templates  # Templates directory functions as a frontend
from .extensions import (
    admin, bootstrap, mail,
    moment, health, babel,
    db, serializer, assets,
    debugger, register_app_cdn, BaseModel
)
from .encoders import AppJSONEncoder
from .server import build_routes

""" Create the app """
app = Flask(
    __name__,
    template_folder='../templates',
    static_folder="../static",
)

""" Bind config + security settings to app """
import modules.core as app_core


""" Init + Bind extensions to app """
# Ordering is important.
admin.init_app(app)
babel.init_app(app)
bootstrap.init_app(app)
db.init_app(app)
serializer.init_app(app)
mail.init_app(app)
moment.init_app(app)
health.init_app(app, "/healthcheck")
register_app_cdn(app)
assets.init_app(app)   # Manage JavaScript bundles
templates.nav.init_app(app)

# Inject db session into all models
BaseModel.set_session(db.session)

# Enable/Disable development extensions
if app.debug:
    debugger.init_app(app)

# Module imports
app_core.after_db_init()
import modules.celery_tasks
import modules.report

# Add local HTML
app.register_blueprint(templates.frontend_bp)

# Register JSON encoder
app.json_encoder = AppJSONEncoder

# Add server's static files to be bundled and minified
js = Bundle(
    'js/selectBox.js', 'js/gridArea.js',
    'js/dtSelector.js',
    filters='jsmin', output='gen/packed.js'
)
css = Bundle(
    'css/style.css',
    filters='cssmin', output='gen/all.css'
)
assets.register('js_all', js)
assets.register('css_all', css)
