# backend/__init__.py
from flask import Flask

from backend.services import (
    init_notifications, init_logging, make_dir, add_cdns
)
from backend.services.extensions import (
    bootstrap, nav, mail,
    moment, health, babel,
    db, ma
)


def create_application(*cfg):
    """
    Creates the server that the html pages interact with.
    """
    app_instance = Flask(
        __name__,
        instance_relative_config=True,
        template_folder='../../static/templates',
        static_folder="../../static",
    )

    # Settings - cfg settings override environment and default
    app_instance.config.from_object('backend.config.celery_config.Config')
    app_instance.config.from_object('backend.config.default_config.DevelopmentConfig')
    app_instance.config.from_pyfile('app.cfg', silent=False)
    for config_file in cfg:
        app_instance.config.from_pyfile(config_file, silent=True)

    if not app_instance.debug:
        app_instance.config.from_object('backend.config.default_config.ProductionConfig')

    # Init + Bind services to app_instance
    # Ordering is important.
    db.init_app(app_instance)
    babel.init_app(app_instance)
    bootstrap.init_app(app_instance)
    nav.init_app(app_instance)
    ma.init_app(app_instance)
    mail.init_app(app_instance)
    moment.init_app(app_instance)
    health.init_app(app_instance, "/healthcheck")

    # Enable production settings
    if not app_instance.debug:
        init_logging(app_instance)
        init_notifications(app_instance, mail)

    make_dir(app_instance.config['TMP_DIR'])

    # Add CDNs for frontend
    add_cdns(app_instance)

    return app_instance

