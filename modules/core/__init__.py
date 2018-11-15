# security/__init__.py
from flask import url_for, Blueprint, flash, redirect
from flask_restful import Api
from flask_security import logout_user

from modules import app
from modules.base_model import BaseModel
from modules.extensions import admin, db, health
from modules.server import build_routes
from .utilities import ExtendedLoginForm, ExtendedRegisterForm, check_local_db, set_logger

# Configure app settings
import modules.core.config_runner

db.init_app(app)
BaseModel.set_session(db.session)

# Add security
import modules.core.security

security_bp = Blueprint('user_bp', __name__)
security_api = Api(security_bp)


@app.route("/logout")
def logout():
    logout_user()
    flash("Logged out!")
    return redirect(url_for("frontend.index"))


with app.app_context():
    # Enable production/development settings
    if not app.debug:
        # Application logger: rotates every 30 days
        set_logger("INFO")
        # SQLAlchemy logger: long term to show history of DB modifications
        set_logger("INFO", name="sqlalchemy.engine", rotating=False)
        # SQLAlchemy logger: long term to show history of DB modifications
        set_logger("INFO", name="app.sqlalchemy", rotating=False)

    """ Bind models and views to db """
    import modules.core.models
    import modules.core.views

    # Creates any models that have been imported
    db.create_all()

    # Register the admin views to the extension
    admin.add_view(
        views.UsersView(
            models.UserModel, db.session, name='Manage Users', category='User Admin'
        )
    )
    admin.add_view(
        views.RolesView(
            models.RolesModel, db.session, name='Manage Privileges', category='User Admin'
        )
    )

app.register_blueprint(security_bp)

# Inject module routes
build_routes(app, security_api, "core")

# Register system checks
health.add_check(check_local_db)

from .utilities import *
