# security/__init__.py
from flask import Blueprint
from flask_restful import Api


from app import app_instance, admin, db
from app.server import build_routes
from .views import SLAReportView


sla_report_bp = Blueprint('sla_report_bp', __name__)
sla_report_api = Api(sla_report_bp)


""" Create models for module in dB """
with app_instance.app_context():
    from app.report.models import (
        SlaReportModel, sla_report_model, TablesLoaded,
        CallTableModel, EventTableModel, ClientModel
    )
    # Creates any models that have been imported
    db.create_all()

    # Register the admin views to the extension
    admin.add_view(SLAReportView(SlaReportModel, db.session, name='SLA report', category="Reports"))


app_instance.register_blueprint(sla_report_bp)

# Inject module routes
build_routes(app_instance, sla_report_api, "report")
