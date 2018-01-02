# report/api.py
from flask import g
from flask_restful import Resource


from app.util.tasks import return_task
from .tasks import report_task


class Report(Resource):

    decorators = [return_task]

    def get(self):
        print('Hit GET Report API')
        args = g.parser.parse_args()
        return report_task(
            args['task'],
            start_time=args['start_time'],
            end_time=args['end_time']
        )

    def put(self):
        print('Hit PUT Report API')
        args = g.parser.parse_args()
        return report_task(
            args['task'],
            start_time=args['start_time'],
            end_time=args['end_time']
        )
