# data/api.py
from flask_restful import Resource, reqparse


from backend.services.app_tasks import return_task, to_datetime, to_list
from .tasks import data_task


class DataAPI(Resource):

    decorators = [return_task]

    def __init__(self):
        parser = reqparse.RequestParser()
        parser.add_argument(
            'task', dest='task', help='A task to complete.'
        )
        parser.add_argument(
            'start_time', type=to_datetime,
            help='Start time for data interval.'
        )
        parser.add_argument(
            'end_time', type=to_datetime,
            help='End time for data interval.'
        )
        parser.add_argument(
            'clients', type=to_list,
            help='List of clients to be row values.'
        )
        self.args = parser.parse_args()
        super().__init__()

    def __del__(self):
        pass

    def get(self):
        print('Hit GET Data API')
        return data_task(
            self.args['task'],
            start_time=self.args['start_time'],
            end_time=self.args['end_time']
        )

    def put(self):
        print('Hit PUT Data API')

        return data_task(
            self.args['task'],
            start_time=self.args['start_time'],
            end_time=self.args['end_time']
        )