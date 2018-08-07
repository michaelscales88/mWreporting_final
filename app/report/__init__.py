# security/__init__.py
from flask import Blueprint
from flask_restful import Api

from app import app_instance, admin, db
from app.server import build_routes
from .tasks import register_tasks
from .views import (
    SLAReportView, ClientView, CallDataView,
    EventDataView, TablesLoadedView, ClientManagerView
)

sla_report_bp = Blueprint('sla_report_bp', __name__)
sla_report_api = Api(sla_report_bp)


""" Create models for module in dB """
with app_instance.app_context():
    from app.report.models import (
        SlaReportModel, TablesLoadedModel, ClientManager,
        CallTableModel, EventTableModel, ClientModel
    )

    # Init task scheduling
    register_tasks(app_instance)

    # Creates any models that have been imported
    db.create_all()

    # Report Views: All
    admin.add_view(SLAReportView(SlaReportModel, db.session, name='SLA Report', category="Data Admin"))
    
    # Client Manager Views: Manager Area
    admin.add_view(ClientManagerView(ClientManager, db.session, name="Client Managers"))

    # Client Manager Views: Admin Area
    admin.add_view(ClientView(ClientModel, db.session, name='Add/Remove Clients', category="Admin"))

    # Report Data Views: Admin Area
    admin.add_view(TablesLoadedView(TablesLoadedModel, db.session, name='Loaded Data', category="Data Admin"))
    admin.add_view(CallDataView(CallTableModel, db.session, name='Call Data', category="Data Admin"))
    admin.add_view(EventDataView(EventTableModel, db.session, name='Event Data', category="Data Admin"))


app_instance.register_blueprint(sla_report_bp)

# Inject module routes
build_routes(app_instance, sla_report_api, "report")
