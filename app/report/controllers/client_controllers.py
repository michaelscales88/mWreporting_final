# client/api.py
from flask_restful import Resource, reqparse

from app.utilities import return_task, to_bool
from ..models import ClientModel


class ClientAPI(Resource):

    decorators = [return_task]

    def __init__(self):
        parser = reqparse.RequestParser()
        parser.add_argument("status", type=to_bool, default=True)
        self.args = parser.parse_args()
        super().__init__()

    def get(self):
        print('Hit GET Client API')
        clients = ClientModel.query.filter(ClientModel.active == self.args['status']).all()
        return clients
