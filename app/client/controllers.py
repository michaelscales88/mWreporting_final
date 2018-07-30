# client/api.py
from flask_restful import Resource, reqparse
from sqlalchemy.exc import DatabaseError
from flask_security import login_required


from app.services.app_tasks import return_task, to_bool
from .tasks import add_client, disable_client, get_clients
from .models import ClientModel


class ClientAPI(Resource):

    decorators = [return_task]

    def __init__(self):
        parser = reqparse.RequestParser()
        parser.add_argument(
            'client_name', location='form',
            help='A client to change.'
        )
        parser.add_argument(
            'client_ext', location='form',
            help='The client number to change.'
        )
        parser.add_argument(
            'is_active', location='form', type=to_bool,
            help='Active clients.'
        )
        self.args = parser.parse_args()
        super().__init__()

    def __del__(self):
        try:
            ClientModel.session.commit()
        # Rollback a bad session
        except DatabaseError:
            ClientModel.session.rollback()

    def get(self):
        print('Hit GET Client API')
        return get_clients()

    @login_required
    def put(self):
        print('hit PUT Client API', self.args)
        return add_client(self.args['client_name'], self.args['client_ext'])

    @login_required
    def delete(self):
        print('hit DELETE Client API')
        return disable_client(self.args['client_name'], self.args['client_ext'])
