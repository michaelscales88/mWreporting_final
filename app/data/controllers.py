# data/api.py
from flask_restful import Resource, reqparse
import datetime

from app.services.app_tasks import return_task, to_datetime, to_list
from .tasks import data_task


class DataAPI(Resource):

    decorators = [return_task]

    def __init__(self):
        parser = reqparse.RequestParser()
        parser.add_argument(
            'task', location='form', help='A task to complete.'
        )
        parser.add_argument(
            'start_time', location='form', type=to_datetime,
            help='Start time for data interval.'
        )
        parser.add_argument(
            'end_time', location='form', type=to_datetime,
            help='End time for data interval.'
        )
        parser.add_argument('table', location='form')
        self.args = parser.parse_args()
        super().__init__()

    def __del__(self):
        pass

    def get(self):
        print("hit get", datetime.datetime.utcnow(), self.args, flush=True)
        """

        :return:
        """
        return "c_call", "c_event"

    def put(self):
        print("hit put", datetime.datetime.utcnow(), self.args, flush=True)

        """

        :return:
        """
        return data_task(
            self.args['task'],
            start_time=self.args['start_time'],
            end_time=self.args['end_time'],
            table=self.args['table']
        )
