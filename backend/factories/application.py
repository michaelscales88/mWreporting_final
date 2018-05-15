# backend/__init__.py
from flask import Flask


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

    return app_instance

