# app/backend.py
from flask import Blueprint
from flask_restful import Api


api_bp = Blueprint('backend', __name__)
api = Api(api_bp)


from .client.api import ClientAPI
from .data.api import DataAPI
from .report.api import ReportAPI


# Register the endpoint to the api
api.add_resource(ClientAPI, '/client-api')
api.add_resource(DataAPI, '/data-api')
api.add_resource(ReportAPI, '/report-api')

