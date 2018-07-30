# config/server.py
from flask_assets import Bundle
from flask_login.utils import logout_user

# Modules
# from .backend import api_bp
from .extensions import (
    health, db, assets
)
# from .frontend import frontend_bp
from .services import (
    get_local_healthcheck, get_data_healthcheck, BaseModel
)
from .encoders import AppJSONEncoder


def configure_server(server_instance):
    """
    Uses the server's context to build all the components of the server.
    This allows the blueprints to access the instance of server that they're
    a part of.
    :param server_instance: Flask App
    :return: Configured Flask App
    """
    print("Starting server setup.")
    with server_instance.app_context():

        # Register system checks
        health.add_check(get_local_healthcheck)
        health.add_check(get_data_healthcheck)

        # Register JSON encoder
        server_instance.json_encoder = AppJSONEncoder

        # Register persistent celery tasks
        # from app.data.tasks import register_tasks as register_data_tasks
        # from app.report.tasks import register_tasks as register_report_tasks
        # register_data_tasks(server_instance)
        # register_report_tasks(server_instance)

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

        print("Completed server setup.")
