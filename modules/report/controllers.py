# report/api.py
from flask import jsonify

from modules.base_resource import BaseResource

from .models import ClientModel, ClientManager
from .serializers import ClientModelSchema
from .tasks import get_summary_sla_report, get_sla_report


class SummaryReportAPI(BaseResource):

    def post(self):
        return get_summary_sla_report(
            start_time=self.args['start_time'],
            end_time=self.args['end_time'],
            clients=self.args['clients']
        )


class SLAReportAPI(BaseResource):

    def post(self):
        report_frame = get_sla_report(
            start_time=self.args['start_time'],
            end_time=self.args['end_time'],
            clients=self.args['clients']
        )
        data = report_frame.to_dict(orient='split')['data']
        columns = list(report_frame)
        return jsonify(data=data, columns=columns)


class SLAClientAPI(BaseResource):

    def __init__(self):
        self.schema = ClientModelSchema(many=True)
        super().__init__()

    def get(self):
        all_clients = ClientModel.query.filter(ClientModel.active == self.args['active']).all()
        print(all_clients)
        return jsonify(
            data=self.schema.dump(all_clients).data
        )

    def post(self):
        manager = ClientManager.find(self.current_user)
        managers_clients = manager.clients if manager else []
        return jsonify(
            data=self.schema.dump(managers_clients).data
        )
