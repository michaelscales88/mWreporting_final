# config/server.py
from importlib import import_module


def build_routes(server_instance, api, module_name):
    with server_instance.app_context():
        api_config = server_instance.config.get("{module}_MODULE_ROUTES".format(module=module_name.upper()))
        if api_config:
            resources = import_module("modules.{module}.controllers".format(module=module_name))
            if resources:
                for api_name in api_config.keys():
                    if api_config[api_name].get("url") is None:
                        continue
                    api_resource = getattr(resources, api_name)
                    api.add_resource(
                        api_resource, *(api_config[api_name]['url'], api_config[api_name]['url'] + '/')
                    )
            else:
                print("Error: Failed to load routes for the {module} module.".format(module=module_name))


def register_with_app(app, bp, api):
    app.register_blueprint(bp)

    # Reflect and Inject module routes
    build_routes(app, api, str(bp.name))
