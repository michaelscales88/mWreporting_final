# backend/__init__.py
from flask import render_template


from .server import (
    server, celery, db, init_db,
    health, moment, mail, nav,
    send_async_email, bind_model_session
)
from .services import (
    add_cdns, make_dir, get_local_healthcheck,
    get_data_healthcheck, init_logging
)

# Modules
from .backend import api_bp
from .frontend import frontend_bp


server.register_blueprint(api_bp)
server.register_blueprint(frontend_bp)

health.add_check(get_local_healthcheck)
health.add_check(get_data_healthcheck)

if not server.debug:
    server.config.from_object('backend.default_config.ProductionConfig')
    init_logging(server, mail)


# Set up the session for all app models
bind_model_session()


# Configuration for APP
@server.before_first_request
def startup_setup():
    print("Starting server setup.")
    # Ensure the tmp directory exists
    make_dir(server.config['TMP_DIR'])

    # Make database and tables
    init_db()

    # Add CDNs for frontend
    add_cdns(server)

    # Init scheduled celery tasks.
    from .data.tasks import register_tasks as register_data_tasks
    from .report.tasks import register_tasks as register_report_tasks
    register_data_tasks(server)
    register_report_tasks(server)

    print("Completed server setup.")


# Error pages
@server.errorhandler(404)
def not_found_error(error):
    return render_template('404.html', title='Page Not Found'), 404


@server.errorhandler(500)
def internal_error(error):
    return render_template('500.html', title='Resource Error'), 500
