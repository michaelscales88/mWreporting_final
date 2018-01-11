# app/backend.py
from flask import Blueprint
from flask_restful import Api


api_bp = Blueprint('backend', __name__)
api = Api(api_bp)


from .client.api import Client
from .data.api import Data
from .report.api import Report


# Register the endpoint to the api
api.add_resource(Client, '/client-api')
api.add_resource(Data, '/data-api')
api.add_resource(Report, '/report-api')

