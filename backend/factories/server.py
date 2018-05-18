# backend/server.py
import datetime

from flask import render_template, redirect, url_for, flash
from flask_assets import Bundle
from flask_login.utils import logout_user
from flask_user import SQLAlchemyAdapter, UserManager

# Modules
from backend.backend import api_bp
from backend.frontend import frontend_bp
from backend.services import (
    get_local_healthcheck,
    get_data_healthcheck, AppJSONEncoder, BaseModel
)
from backend.services.extensions import (
    health, db, assets
)


def create_server(server_instance):
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

        # Configure DB
        # Import models that need to be created
        from backend.client.models import ClientModel
        from backend.data.models import EventTableModel, CallTableModel, TablesLoaded
        from backend.report.models import SlaReportModel
        from backend.user.models import UserModel, MyRegisterForm
        db.create_all()

        # Inject session that models will use
        BaseModel.set_session(db.session)

        # Setup User/Login Manager
        db_adapter = SQLAlchemyAdapter(db, UserModel)  # Register the User model
        user_manager = UserManager(
            app=server_instance,
            db_adapter=db_adapter,
            register_form=MyRegisterForm
        )  # Initialize Flask-User

        # Create 'mindwireless@gmail.com' Admin
        if UserModel.get(1) is None:
            user = UserModel.create(
                username='admin',
                password=user_manager.hash_password(server_instance.config['ADMIN_PASSWORD']),
                email=server_instance.config['ADMINS'][0],
                confirmed_at=datetime.datetime.utcnow(),
                first_name="Admin",
                last_name="User"
            )
            print("created user", user)
            user.session.commit()

        @user_manager.login_manager.user_loader
        def load_user(user_id):
            try:
                return UserModel.get(user_id)
            except Exception as e:
                raise e

        @server_instance.route("/logout")
        def logout():
            logout_user()
            flash("Logged out!")
            return redirect(url_for("frontend.serve_pages", page="index"))

        # Error pages
        @server_instance.errorhandler(404)
        def not_found_error(error):
            flash("Could not find the page you were looking for.", 'error')
            return redirect(url_for("frontend.serve_pages", page="index"))

        @server_instance.errorhandler(500)
        def internal_error(error):
            return render_template('500.html', title='Resource Error'), 500

        # Register API rules with the server
        server_instance.register_blueprint(frontend_bp)
        server_instance.register_blueprint(
            api_bp,
            url_prefix="/api"
        )

        # Register persistent celery tasks
        from backend.data.tasks import register_tasks as register_data_tasks
        from backend.report.tasks import register_tasks as register_report_tasks
        register_data_tasks(server_instance)
        register_report_tasks(server_instance)

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
        return server_instance

