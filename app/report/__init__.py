# security/__init__.py
from flask import Blueprint
from flask_restful import Api


from app import app_instance, admin, db
from app.server import build_routes


sla_report_bp = Blueprint('sla_report_bp', __name__)
sla_report_api = Api(sla_report_bp)


""" Create models for module in dB """
with app_instance.app_context():
    from app.scheduled_tasks.models.models import ScheduleItemModel
    # Creates any models that have been imported
    db.create_all()

    # Register the admin views to the extension
    # admin.add_view(ScheduledItemsView(ScheduleItemModel, db.session, name='Scheduled Reports'))


app_instance.register_blueprint(sla_report_api)

# Inject module routes
build_routes(app_instance, sla_report_api, "report")
