# data/api.py
from flask import g
from flask_restful import Resource


from app.util.tasks import return_task
from .tasks import data_task


class Data(Resource):

    decorators = [return_task]

    def get(self):
        print('Hit GET Data API')
        args = g.parser.parse_args()
        return data_task(
            args['task'],
            start_time=args['start_time'],
            end_time=args['end_time']
        )

    def put(self):
        print('Hit PUT Data API')
        args = g.parser.parse_args()
        return data_task(
            args['task'],
            start_time=args['start_time'],
            end_time=args['end_time']
        )
