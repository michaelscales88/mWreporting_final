# report/api.py
from flask import g, current_app
from flask_restful import Resource


from app.database import get_session
from app.util.tasks import return_task, to_datetime, to_list
from .tasks import report_task


class Report(Resource):

    decorators = [return_task]

    def __init__(self):
        g.local_session = get_session(current_app.config['SQLALCHEMY_DATABASE_URI'])
        g.parser.add_argument(
            'start_time', type=to_datetime,
            help='Start time for data interval.'
        )
        g.parser.add_argument(
            'end_time', type=to_datetime,
            help='End time for data interval.'
        )
        g.parser.add_argument(
            'clients', type=to_list,
            help='List of clients to be row values.'
        )
        super().__init__()

    def get(self):
        print('Hit GET Report API')
        args = g.parser.parse_args()
        print(args)
        print(type(args['clients']))
        for c in args['clients']:
            print(c)
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
