# security/__init__.py
from flask import url_for, Blueprint, flash, redirect
from flask_restful import Api
from flask_security import logout_user

# Add security
import modules.core.security
from modules import app
from modules.extensions import admin, health
from modules.utilities.health_check import check_local_db
from modules.utilities.logger import set_logger
from modules.utilities.server import build_routes
from .encoders import AppJSONEncoder

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

    # session = get_session(app)[1]

    # from modules import session

    # Register the admin views to the extension
    admin.add_view(
        views.UsersView(
            models.UserModel,
            models.UserModel.session,
            name='Manage Users', category='User Admin'
        )
    )
    admin.add_view(
        views.RolesView(
            models.RolesModel,
            models.RolesModel.session,
            name='Manage Privileges', category='User Admin'
        )
    )

    # Register JSON encoder
    app.json_encoder = AppJSONEncoder

app.register_blueprint(security_bp)

# Inject module routes
build_routes(app, security_api, "core")

# Register system checks
health.add_check(check_local_db)

