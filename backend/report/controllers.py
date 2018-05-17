# report/api.py
from flask_restful import Resource, reqparse


from backend.services.app_tasks import return_task, to_datetime, to_list
from .tasks import report_task


class ReportAPI(Resource):

    def __init__(self):
        parser = reqparse.RequestParser()
        self.args = parser.parse_args()
        super().__init__()

    def __del__(self):
        pass

    def get(self):
        print('Hit GET Report API', self.args)
        return []


class SlaReportAPI(Resource):

    decorators = [return_task]

    def __init__(self):
        parser = reqparse.RequestParser()
        parser.add_argument(
            'task', help='A task to complete.'
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
        print('Hit GET Report API', self.args)
        return report_task(
            self.args['task'],
            start_time=self.args['start_time'],
            end_time=self.args['end_time'],
            clients=self.args['clients']
        )

    def put(self):
        print('Hit PUTS Report API', self.args)
        return report_task(
            self.args['task'],
            start_time=self.args['start_time'],
            end_time=self.args['end_time'],
            clients=self.args['clients']
        )
