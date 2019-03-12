# security/__init__.py
import warnings

from flask import Blueprint
from flask_restful import Api

from modules import app, register_with_app
from modules.extensions import admin

report_bp = Blueprint('report', __name__)
report_api = Api(report_bp)

""" Create models for module in dB """
with app.app_context():
    import modules.report.models
    import modules.report.views

    # Add home link by url
    admin.add_category("Reports")
    admin.add_sub_category("SLA Reports", "Reports")
    admin.add_sub_category("Clients/Managers", "Reports")

    # Register the admin views to the extension
    # Ignore warning messages from overridden fields
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', 'Fields missing from ruleset', UserWarning)

        # Report Views: All
        report_view = views.SLAReportView(
            models.SlaReportModel,
            models.SlaReportModel.session,
            name='View Reports', category="SLA Reports"
        )
        summary_report_view = views.SLASummaryReportView(
            models.SummarySLAReportModel,
            models.SummarySLAReportModel.session,
            name='Summary Reports', category="Reports"
        )

        # General: Admin Area
        clients_view = views.ClientView(
            models.ClientModel,
            models.ClientModel.session,
            name='Add/Remove Clients', category="Clients/Managers"
        )
        cm_view = views.ClientManagerView(
            models.ClientManager,
            models.ClientManager.session,
            name="Client Managers", category="Clients/Managers"
        )

        # Report: Admin Area
        report_data_view = views.TablesLoadedView(
            models.TablesLoadedModel,
            models.TablesLoadedModel.session,
            name='Add/Remove Report Data', category="SLA Reports"
        )
        calls_view = views.CallDataView(
            models.CallTableModel,
            models.CallTableModel.session,
            name='View Raw Call Data', category="SLA Reports"
        )
        events_view = views.EventDataView(
            models.EventTableModel,
            models.EventTableModel.session,
            name='View Raw Event Data', category="SLA Reports"
        )

        admin.add_views(
            report_view, summary_report_view,
            clients_view, cm_view, report_data_view,
            calls_view, events_view
        )


register_with_app(app, report_bp, report_api)
