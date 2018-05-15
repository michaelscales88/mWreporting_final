# backend/server.py
from flask import render_template
from flask_user import SQLAlchemyAdapter
from werkzeug.security import safe_str_cmp


from backend.services import (
    add_cdns, make_dir, get_local_healthcheck,
    get_data_healthcheck, init_logging,
    AppJSONEncoder, BaseModel, init_notifications
)
from backend.services.extensions import (
    bootstrap, nav, mail,
    moment, health, babel,
    user_manager, jwt
)

# Modules
from backend.backend import api_bp
from backend.frontend import frontend_bp


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

        # Enable production settings
        if not server_instance.debug:
            init_logging(server_instance)
            init_notifications(server_instance, mail)

        make_dir(server_instance.config['TMP_DIR'])

        # Init Services
        babel.init_app(server_instance)
        bootstrap.init_app(server_instance)
        nav.init_app(server_instance)
        mail.init_app(server_instance)
        moment.init_app(server_instance)
        health.init_app(server_instance, "/healthcheck")

        # Add CDNs for frontend
        add_cdns(server_instance)

        # Register system checks
        health.add_check(get_local_healthcheck)
        health.add_check(get_data_healthcheck)

        # Register JSON encoder
        server_instance.json_encoder = AppJSONEncoder

        # Configure DB
        from backend.services.extensions import db
        db.init_app(server_instance)

        # Import models that need to be created
        from backend.client.models import ClientModel
        from backend.data.models import EventTableModel, CallTableModel, TablesLoaded
        from backend.report.models import SlaReportModel
        from backend.users.models import User, MyRegisterForm
        db.create_all()

        # Setup User/Login Manager
        db_adapter = SQLAlchemyAdapter(db, User)  # Register the User model
        user_manager.init_app(
            server_instance,
            db_adapter=db_adapter,
            register_form=MyRegisterForm
        )  # Initialize Flask-User

        @user_manager.login_manager.request_loader
        def load_user_from_request(request):
            # first, try to login using the api_key url arg
            api_key = request.args.get('api_key')
            if api_key:
                is_valid, has_expired, user_id = user_manager.verify_token(api_key, 300)
                # TODO: Update this to current_app
                if not has_expired and is_valid:
                    user = user_manager.get_user_by_id(user_id)
                    if user:
                        return user
            return None

        # Error pages
        @server_instance.errorhandler(404)
        def not_found_error(error):
            return render_template('404.html', title='Page Not Found'), 404

        @server_instance.errorhandler(500)
        def internal_error(error):
            return render_template('500.html', title='Resource Error'), 500

        # Register API rules with the server
        server_instance.register_blueprint(api_bp)
        server_instance.register_blueprint(frontend_bp)

        # Register persistent celery tasks
        from backend.data.tasks import register_tasks as register_data_tasks
        from backend.report.tasks import register_tasks as register_report_tasks
        register_data_tasks(server_instance)
        register_report_tasks(server_instance)

        # Inject session that models will use
        BaseModel.set_session(db.session)
        print("Completed server setup.")
        return server_instance

