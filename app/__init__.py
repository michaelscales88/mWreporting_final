# app/__init__.py
from flask import Flask

import templates  # Templates directory functions as a frontend
from app.extensions import (
    admin, bootstrap, mail,
    moment, health, babel,
    db, serializer, assets,
    debugger, register_app_cdn, BaseModel
)
from .server import configure_server

""" Create the app """
app_instance = Flask(
    __name__,
    template_folder='../templates',
    static_folder="../static",
)

""" Bind config + security settings to app """
import app.core as app_core


""" Init + Bind extensions to app """
# Ordering is important.
admin.init_app(app_instance)
babel.init_app(app_instance)
bootstrap.init_app(app_instance)
db.init_app(app_instance)
serializer.init_app(app_instance)
mail.init_app(app_instance)
moment.init_app(app_instance)
health.init_app(app_instance, "/healthcheck")
register_app_cdn(app_instance)
assets.init_app(app_instance)   # Manage JavaScript bundles
templates.nav.init_app(app_instance)

# Inject db session into all models
BaseModel.set_session(db.session)

# Enable/Disable development extensions
if app_instance.debug:
    debugger.init_app(app_instance)

# Module imports
app_core.after_db_init()
import app.celery_tasks
import app.report

# Add local HTML
app_instance.register_blueprint(templates.frontend_bp)

configure_server(app_instance)
