# client/api.py
from flask_restful import Resource, reqparse
from sqlalchemy.exc import DatabaseError


from app.services.app_tasks import return_task
from .tasks import client_task
from .models import ClientModel


class ClientAPI(Resource):

    decorators = [return_task]

    def __init__(self):
        parser = reqparse.RequestParser()
        parser.add_argument(
            'task', dest='task', help='A task to complete.'
        )
        parser.add_argument(
            'client_name', location='form',
            help='A client to change.'
        )
        parser.add_argument(
            'client_ext', location='form',
            type=int, help='The client number to change.'
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
        return client_task(
            self.args['task'],
            client_name=self.args['client_name'],
            client_ext=self.args['client_ext']
        )

    def put(self):
        print('hit PUT Client API')
        return client_task(
            self.args['task'],
            client_name=self.args['client_name'],
            client_ext=self.args['client_ext']
        )

