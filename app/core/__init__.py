# security/__init__.py
from flask import url_for, Blueprint, flash, redirect
from flask_restful import Api
from flask_admin import helpers
from flask_security import Security, SQLAlchemyUserDatastore, logout_user

from app import app_instance
from app.server import build_routes
from .views import RolesView, UsersView
from .models import UserModel, RolesModel, users_roles_association
from .utilities import ExtendedLoginForm, ExtendedRegisterForm
from app.extensions import admin, db

# Configure app settings
import app.core.config_runner

security_bp = Blueprint('user_bp', __name__)
security_api = Api(security_bp)


@app_instance.route("/logout")
def logout():
    logout_user()
    flash("Logged out!")
    return redirect(url_for("frontend_bp.serve_pages", page="index"))


def after_db_init():
    """ Create models for module in dB """
    with app_instance.app_context():
        # Creates any models that have been imported
        db.create_all()

        # Manage user roles and security
        user_datastore = SQLAlchemyUserDatastore(db, UserModel, RolesModel)
        security = Security(app_instance, user_datastore,
                            login_form=ExtendedLoginForm,
                            register_form=ExtendedRegisterForm)

        @security.context_processor
        def security_context_processor():
            return dict(
                admin_base_template=admin.base_template,
                admin_view=admin.index_view,
                h=helpers,
                get_url=url_for
            )

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


app_instance.register_blueprint(security_bp)

# Inject module routes
build_routes(app_instance, security_api, "core")

from .utilities import *
