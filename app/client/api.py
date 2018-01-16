# client/api.py
from flask import g, current_app
from flask_restful import Resource


from app.database import get_session
from app.util.tasks import return_task
from .tasks import client_task


class Client(Resource):

    decorators = [return_task]

    def __init__(self):
        g.local_session = get_session(current_app.config['SQLALCHEMY_DATABASE_URI'])
        g.parser.add_argument(
            'client_name', location='form',
            help='A client to change.'
        )
        g.parser.add_argument(
            'client_ext', location='form',
            type=int, help='The client number to change.'
        )
        super().__init__()

    def get(self):
        print('Hit GET Client API')
        args = g.parser.parse_args()
        print(args)
        return client_task(
            args['task'],
            client_name=args['client_name'],
            client_ext=args['client_ext']
        )

    def put(self):
        print('hit PUT Client API')
        args = g.parser.parse_args()
        return client_task(
            args['task'],
            client_name=args['client_name'],
            client_ext=args['client_ext']
        )

