# data/api.py
from flask import g, current_app
from flask_restful import Resource


from app.database import get_session
from app.util.tasks import return_task, to_datetime
from .tasks import data_task


class Data(Resource):

    decorators = [return_task]

    def __init__(self):
        g.local_session = get_session(current_app.config['SQLALCHEMY_DATABASE_URI'])
        g.ext_session = get_session(current_app.config['EXTERNAL_DATABASE_URI'], readonly=True)
        g.parser.add_argument(
            'start_time', type=to_datetime,
            help='Start time for data interval.'
        )
        g.parser.add_argument(
            'end_time', type=to_datetime,
            help='End time for data interval.'
        )
        g.parser.add_argument(
            'clients', type=str, action='append'
        )
        super().__init__()

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
