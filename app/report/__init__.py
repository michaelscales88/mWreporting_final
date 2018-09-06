# security/__init__.py
from flask import Blueprint
from flask_restful import Api

from app import app_instance, admin, db
from app.server import build_routes
from .tasks import register_default_report_tasks
from .views import (
    SLAReportView, ClientView, CallDataView,
    EventDataView, TablesLoadedView, ClientManagerView,
    SLASummaryReportView
)

sla_report_bp = Blueprint('sla_report_bp', __name__)
sla_report_api = Api(sla_report_bp)


""" Create models for module in dB """
with app_instance.app_context():
    from app.report.models import (
        SlaReportModel, TablesLoadedModel, ClientManager,
        CallTableModel, EventTableModel, ClientModel,
        SummarySLAReportModel
    )

    # Init task scheduling
    register_default_report_tasks(app_instance)

    # Creates any models that have been imported
    db.create_all()

    # Report Views: All
    admin.add_view(SLAReportView(SlaReportModel, db.session, name='SLA Reports', category="SLA Admin"))
    admin.add_view(SLASummaryReportView(SummarySLAReportModel, db.session, name='Summary Reports', category="SLA Admin"))

    # Client Manager Views: Manager Area
    admin.add_view(ClientManagerView(ClientManager, db.session, name="Client Managers", category="User Admin"))

    # Client Manager Views: Admin Area
    admin.add_view(ClientView(ClientModel, db.session, name='Add/Remove Clients', category="SLA Admin"))

    # Report Data Views: Admin Area
    admin.add_view(TablesLoadedView(TablesLoadedModel, db.session, name='Report Data', category="SLA Admin"))
    admin.add_view(CallDataView(CallTableModel, db.session, name='Raw Call Data', category="SLA Admin"))
    admin.add_view(EventDataView(EventTableModel, db.session, name='Raw Event Data', category="SLA Admin"))


app_instance.register_blueprint(sla_report_bp)

# Inject module routes
build_routes(app_instance, sla_report_api, "report")
