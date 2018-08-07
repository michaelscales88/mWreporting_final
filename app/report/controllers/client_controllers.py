# client/api.py
from flask import jsonify
from flask_restful import Resource, reqparse
from flask_security import current_user

from app.utilities import to_bool
from ..models import ClientModel, ClientManager
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
        all_clients = ClientModel.query.filter(ClientModel.active == self.args['active']).all()
        print("all clients", all_clients)
        return jsonify(
            data=self.schema.dump(all_clients).data
        )

    def post(self):
        manager_clients = ClientManager.find(int(current_user.id)).clients
        print("manager clients", manager_clients)
        return jsonify(
            data=self.schema.dump(manager_clients).data
        )
