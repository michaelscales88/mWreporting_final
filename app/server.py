# config/server.py
from importlib import import_module
from flask_assets import Bundle

from .encoders import AppJSONEncoder
from .extensions import health, db, assets
from .services import (
    get_local_healthcheck, get_data_healthcheck, BaseModel,
    add_cdns
)


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

        # Register system checks
        health.add_check(get_local_healthcheck)
        health.add_check(get_data_healthcheck)

        # Add CDN content to application
        add_cdns(server_instance)

        # Inject session into BaseModel
        BaseModel.set_session(db.session)

        # Register JSON encoder
        server_instance.json_encoder = AppJSONEncoder

        # Add server's static files to be bundled and minified
        js = Bundle(
            'js/client.js', 'js/data.js',
            'js/dt-selector.js', 'js/grid-area.js',
            'js/modal-form.js', 'js/multiple-select.js', 'js/report.js',
            filters='jsmin', output='gen/packed.js'
        )
        css = Bundle(
            'css/style.css', 'css/multiple-select.css',
            filters='cssmin', output='gen/all.css'
        )
        assets.register('js_all', js)
        assets.register('css_all', css)
