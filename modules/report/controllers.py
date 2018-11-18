# report/api.py
from flask import jsonify
from flask_restful import Resource, reqparse
from flask_security import current_user

from modules.core import to_datetime, to_list, to_bool
from .models import ClientModel, ClientManager
from .serializers import ClientModelSchema
from .tasks import get_summary_sla_report, get_sla_report


class SummaryReportAPI(Resource):

    def __init__(self):
        parser = reqparse.RequestParser()
        parser.add_argument(
            'start_time', type=to_datetime, location="form",
            help='Start time for data interval.'
        )
        parser.add_argument(
            'end_time', type=to_datetime, location="form",
            help='End time for data interval.'
        )
        parser.add_argument(
            'clients', type=to_list, location="form",
            help='List of clients to be row values.'
        )
        self.args = parser.parse_args()
        super().__init__()

    def post(self):
        return get_summary_sla_report(
            start_time=self.args['start_time'],
            end_time=self.args['end_time'],
            clients=self.args['clients']
        )


class SLAReportAPI(Resource):

    def __init__(self):
        parser = reqparse.RequestParser()
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

    def post(self):
        print("hit post", self.args)
        report_frame = get_sla_report(
            start_time=self.args['start_time'],
            end_time=self.args['end_time'],
            clients=self.args['clients']
        )
        data = report_frame.to_dict(orient='split')['data']
        columns = list(report_frame)
        return jsonify(data=data, columns=columns)


class SLAClientAPI(Resource):

    def __init__(self):
        self.schema = ClientModelSchema(many=True)
        parser = reqparse.RequestParser()
        parser.add_argument("active", type=to_bool, default=True)
        self.args = parser.parse_args()
        super().__init__()

    def get(self):
        all_clients = ClientModel.query.filter(ClientModel.active == self.args['active']).all()
        return jsonify(
            data=self.schema.dump(all_clients).data
        )

    def post(self):
        manager = ClientManager.find(int(current_user.id))
        managers_clients = manager.clients if manager else []
        return jsonify(
            data=self.schema.dump(managers_clients).data
        )
