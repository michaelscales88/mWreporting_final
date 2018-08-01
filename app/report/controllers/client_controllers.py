# client/api.py
from flask import jsonify
from flask_restful import Resource, reqparse

from app.utilities import to_bool
from ..models import ClientModel
from ..serializers import ClientModelSchema


class ClientAPI(Resource):

    # decorators = [return_task]

    def __init__(self):
        self.schema = ClientModelSchema(many=True)
        parser = reqparse.RequestParser()
        parser.add_argument("active", type=to_bool, default=True)
        self.args = parser.parse_args()
        print(self.args)
        super().__init__()

    def get(self):
        clients = ClientModel.query.filter(ClientModel.active == self.args['active']).all()
        return jsonify(
            data=self.schema.dump(clients).data
        )

    def post(self):
        print('Hit POST Client API')
        all_clients = ClientModel.query.filter(ClientModel.active == self.args['active']).all()
        # user_clients = ClientModel.query.filter(ClientModel)
        return jsonify(
            data=self.schema.dump(all_clients).data
        )
