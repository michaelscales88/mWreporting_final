# app/__init__.py
from flask import Flask

from .extensions import (
    admin, bootstrap, mail,
    moment, health, babel,
    db, serializer, assets, debugger
)
from .server import configure_server

"""
Creates the server that the html pages interact with.
"""
app_instance = Flask(
    __name__,
    template_folder='../templates',
    static_folder="../static",
)


""" Bind config + security settings """
import app.config as app_config

""" Init + Bind services to app """
# Ordering is important.
admin.init_app(app_instance)
babel.init_app(app_instance)
bootstrap.init_app(app_instance)
db.init_app(app_instance)
serializer.init_app(app_instance)
mail.init_app(app_instance)
moment.init_app(app_instance)
health.init_app(app_instance, "/healthcheck")

# Manage JavaScript
assets.init_app(app_instance)
app_config.add_cdns(app_instance)

# Enable production/development settings
if app_instance.debug:
    debugger.init_app(app_instance)

# Module imports
import app.report
import app.scheduled_tasks
import app.security

# Add local HTML
import templates as template_routes
app_instance.register_blueprint(template_routes.frontend_bp)
template_routes.nav.init_app(app_instance)


configure_server(app_instance)
