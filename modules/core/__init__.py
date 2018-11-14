# security/__init__.py
from flask import url_for, Blueprint, flash, redirect
from flask_restful import Api
from flask_security import logout_user

from modules import app
from modules.extensions import admin, db, health
from modules.server import build_routes
from .models import UserModel, RolesModel, users_roles_association
from .utilities import ExtendedLoginForm, ExtendedRegisterForm, check_local_db, set_logger
from .views import RolesView, UsersView

# Configure app settings
import modules.core.config_runner

security_bp = Blueprint('user_bp', __name__)
security_api = Api(security_bp)


@app.route("/logout")
def logout():
    logout_user()
    flash("Logged out!")
    return redirect(url_for("frontend_bp.serve_pages", page="index"))


def after_db_init():
    """ Create models for module in dB """
    with app.app_context():
        # Creates any models that have been imported
        db.create_all()

        # Init security for the application
        from .security import user_datastore

        # Create the Admin user
        if not UserModel.find(1):
            user_datastore.create_role(name='_permissions | admin')
            user_datastore.create_role(name='_permissions | manager')
            user_datastore.create_role(name='_permissions | agent')
            user_datastore.create_user(
                username='admin',
                email='admin@email.com',
                password='password',
                first_name='Super',
                last_name='Admin',
                roles=['_permissions | admin']
            )
            db.session.commit()

        # Register the admin views to the extension
        admin.add_view(
            UsersView(
                UserModel, db.session, name='Manage Users', category='User Admin'
            )
        )
        admin.add_view(RolesView(RolesModel, db.session, name='Manage Privileges', category='User Admin'))

        # Enable production/development settings
        if not app.debug:
            # Application logger: rotates every 30 days
            set_logger("INFO")
            # SQLAlchemy logger: long term to show history of DB modifications
            set_logger("INFO", name="sqlalchemy.engine", rotating=False)
            # SQLAlchemy logger: long term to show history of DB modifications
            set_logger("INFO", name="app.sqlalchemy", rotating=False)


app.register_blueprint(security_bp)

# Inject module routes
build_routes(app, security_api, "core")

# Register system checks
health.add_check(check_local_db)

from .utilities import *
