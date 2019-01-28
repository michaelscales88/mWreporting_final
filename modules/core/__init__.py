# security/__init__.py
from flask import url_for, Blueprint, flash, redirect
from flask_restful import Api
from flask_security import logout_user

# Add security
import modules.core.security
from modules import app, register_with_app
from modules.extensions import admin
from .encoders import AppJSONEncoder

security_bp = Blueprint('core', __name__)
security_api = Api(security_bp)


@app.route("/logout")
def logout():
    logout_user()
    flash("Logged out!")
    return redirect(url_for("frontend.index"))


with app.app_context():
    """ Bind models and views to db """
    import modules.core.models
    import modules.core.views

    # Register the admin views to the extension
    admin.add_view(
        views.UsersView(
            models.UserModel,
            models.UserModel.session,
            name='Manage Users', category='Admin'
        )
    )
    admin.add_view(
        views.RolesView(
            models.RolesModel,
            models.RolesModel.session,
            name='Manage User Privileges', category='Admin'
        )
    )

    # Register JSON encoder
    app.json_encoder = AppJSONEncoder


register_with_app(app, security_bp, security_api)
