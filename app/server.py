# config/server.py
from importlib import import_module

from flask_assets import Bundle

from .encoders import AppJSONEncoder
from app.extensions import health, assets


def build_routes(server_instance, api, module_name):
    with server_instance.app_context():
        api_config = server_instance.config.get("{module}_MODULE_ROUTES".format(module=module_name.upper()))
        if api_config:
            resources = import_module("app.{module}.controllers".format(module=module_name))
            for api_name in api_config.keys():
                if api_config[api_name].get("url") is None:
                    continue
                api_resource = getattr(resources, api_name)
                api.add_resource(
                    api_resource, *(api_config[api_name]['url'], api_config[api_name]['url'] + '/')
                )
        else:
            print("Error: Failed to load routes for the {module} module.".format(module=module_name))


def configure_server(server_instance):
    """
    Uses the server's context to build all the components of the server.
    This allows the blueprints to access the instance of server that they're
    a part of.
    :param server_instance: Flask App
    :return: Configured Flask App
    """
    with server_instance.app_context():
        from app.core.utilities import check_local_db, set_logger

        # Enable production/development settings
        if not server_instance.debug:
            # Application logger: rotates every 30 days
            set_logger("INFO")
            # SQLAlchemy logger: long term to show history of DB modifications
            set_logger("INFO", name="sqlalchemy.engine", rotating=False)
            # SQLAlchemy logger: long term to show history of DB modifications
            set_logger("INFO", name="app.sqlalchemy", rotating=False)

        # Register system checks
        health.add_check(check_local_db)

        # Register JSON encoder
        server_instance.json_encoder = AppJSONEncoder

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
