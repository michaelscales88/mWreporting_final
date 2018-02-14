# backend/__init__.py
from flask import render_template


from .server import (
    app, db, init_db, health,
    moment, celery, nav, mail,
    BaseModel, send_async_email
)
from .services import (
    add_cdns, make_dir, get_local_healthcheck,
    get_data_healthcheck, init_logging
)

# Modules
from .backend import api_bp
from .frontend import frontend_bp


app.register_blueprint(api_bp)
app.register_blueprint(frontend_bp)

health.add_check(get_local_healthcheck)
health.add_check(get_data_healthcheck)


# Configuration for APP
@app.before_first_request
def startup_setup():
    # Ensure the tmp directory exists
    make_dir(app.config['TMP_DIR'])

    # Make database and tables
    init_db()

    # Add CDNs for frontend
    add_cdns(app)

    # Inject session to be used by Models
    BaseModel.set_session(db.session)

    if not app.debug:
        app.config.from_object('backend.default_config.ProductionConfig')
        init_logging(app, mail)

    # Init tasks for application


# Error pages
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html', title='Page Not Found'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html', title='Resource Error'), 500
