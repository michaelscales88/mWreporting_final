# security/__init__.py
from flask import Blueprint
from flask_restful import Api


from app import app_instance, admin, db
from app.server import build_routes
from .views import SLAReportView, ClientView, CallDataView, EventDataView, TablesLoadedView
from .tasks import register_tasks

sla_report_bp = Blueprint('sla_report_bp', __name__)
sla_report_api = Api(sla_report_bp)


""" Create models for module in dB """
with app_instance.app_context():
    from app.report.models import (
        SlaReportModel, TablesLoadedModel, ClientManagerAssociation,
        CallTableModel, EventTableModel, ClientModel
    )

    # Init task scheduling
    register_tasks(app_instance)

    # Creates any models that have been imported
    db.create_all()

    # Report Views: All
    admin.add_view(SLAReportView(SlaReportModel, db.session, name='SLA Report', category="Reports"))
    
    # Client Manager Views: Manager Area
    admin.add_view(ClientView(ClientManagerAssociation, db.session, name='Clients'))

    # Client Manager Views: Admin Area
    admin.add_view(ClientView(ClientModel, db.session, name='Modify Clients'))

    # Report Data Views: Admin Area
    admin.add_view(TablesLoadedView(TablesLoadedModel, db.session, name='Loaded Data', category="Reports"))
    admin.add_view(CallDataView(CallTableModel, db.session, name='Call Data', category="Reports"))
    admin.add_view(EventDataView(EventTableModel, db.session, name='Event Data', category="Reports"))


app_instance.register_blueprint(sla_report_bp)

# Inject module routes
build_routes(app_instance, sla_report_api, "report")
