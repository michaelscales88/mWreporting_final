# config/server.py
from importlib import import_module

from flask_assets import Bundle

from .encoders import AppJSONEncoder
from .extensions import health, assets
from .utilities import check_local_db


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
    from .config import init_loggers
    from .extensions.mailer import init_notifications
    """
    Uses the server's context to build all the components of the server.
    This allows the blueprints to access the instance of server that they're
    a part of.
    :param server_instance: Flask App
    :return: Configured Flask App
    """
    with server_instance.app_context():

        # Enable production/development settings
        if server_instance.debug:
            init_loggers("DEBUG")
        else:
            init_loggers("INFO")
            init_notifications()

        # Register system checks
        health.add_check(check_local_db)

        # Register JSON encoder
        server_instance.json_encoder = AppJSONEncoder

        # Add server's static files to be bundled and minified
        js = Bundle(
            'js/selectBox.js', 'js/grid-area.js',
            'js/dt-selector.js',
            filters='jsmin', output='gen/packed.js'
        )
        css = Bundle(
            'css/style.css',
            filters='cssmin', output='gen/all.css'
        )
        assets.register('js_all', js)
        assets.register('css_all', css)
