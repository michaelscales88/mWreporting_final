# client/api.py
from flask import g
from flask_restful import Resource


from app.util.tasks import return_task
from .tasks import client_task


class Client(Resource):

    decorators = [return_task]

    def get(self):
        print('Hit GET Client API')
        args = g.parser.parse_args()
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

