# backend/backend.py
from flask import Blueprint
from flask_restful import Api


api_bp = Blueprint('backend', __name__)
api = Api(api_bp)


from .client import ClientAPI
from .data import DataAPI
from .report import SlaReportAPI, ReportAPI
from .users import UserAPI


# Register the endpoint to the api
api.add_resource(ClientAPI, '/api/client')
api.add_resource(DataAPI, '/api/data')
api.add_resource(SlaReportAPI, '/api/sla-report')
api.add_resource(ReportAPI, '/api/report')
api.add_resource(UserAPI, '/api/user')

