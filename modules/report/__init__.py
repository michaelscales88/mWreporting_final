# security/__init__.py
from flask import Blueprint
from flask_restful import Api

from modules import app
from modules.extensions import admin, get_session
from modules.server import build_routes
from .tasks import register_default_report_tasks
from .views import (
    SLAReportView, ClientView, CallDataView,
    EventDataView, TablesLoadedView, ClientManagerView,
    SLASummaryReportView
)

sla_report_bp = Blueprint('sla_report_bp', __name__)
sla_report_api = Api(sla_report_bp)


""" Create models for module in dB """
with app.app_context():
    from modules.report.models import (
        SlaReportModel, TablesLoadedModel, ClientManager,
        CallTableModel, EventTableModel, ClientModel,
        SummarySLAReportModel
    )

    # Init task scheduling
    register_default_report_tasks(app)

    # Report Views: All
    admin.add_view(
        SLAReportView(
            SlaReportModel, get_session(app)[1],
            name='SLA Reports', category="SLA Admin"
        )
    )
    admin.add_view(
        SLASummaryReportView(
            SummarySLAReportModel, get_session(app)[1],
            name='Summary Reports', category="SLA Admin"
        )
    )

    # Client Manager Views: Manager Area
    admin.add_view(
        ClientManagerView(
            ClientManager, get_session(app)[1],
            name="Client Managers", category="User Admin"
        )
    )

    # Client Manager Views: Admin Area
    admin.add_view(
        ClientView(
            ClientModel, get_session(app)[1],
            name='Add/Remove Clients', category="SLA Admin"
        )
    )

    # Report Data Views: Admin Area
    admin.add_view(
        TablesLoadedView(
            TablesLoadedModel, get_session(app)[1],
            name='Report Data', category="SLA Admin"
        )
    )
    admin.add_view(
        CallDataView(
            CallTableModel, get_session(app)[1],
            name='Raw Call Data', category="SLA Admin"
        )
    )
    admin.add_view(
        EventDataView(
            EventTableModel, get_session(app)[1],
            name='Raw Event Data', category="SLA Admin"
        )
    )


app.register_blueprint(sla_report_bp)

# Inject module routes
build_routes(app, sla_report_api, "report")
