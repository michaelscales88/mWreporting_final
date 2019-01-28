# report/api.py
from flask import jsonify

from modules.base.base_resource import BaseResource

from .models import ClientModel
from .serializers import clients_schema
from .worker import get_summary_sla_report, get_sla_report


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
        data = report_frame.get_ordered_dict(orient='split')['data']
        columns = list(report_frame)
        return jsonify(data=data, columns=columns)


class SLAClientAPI(BaseResource):

    def get(self):
        all_clients = ClientModel.query.filter(ClientModel.active == self.args['active']).all()
        return jsonify(
            data=clients_schema.dump(all_clients).data
        )

    # @user_auth
    def post(self):
        # print(request.form['_user_id'])
        return jsonify(
            data=[]
        )
        # if self.current_user_id:
        # if False:
        #     manager = ClientManager.find(self.current_user_id)
        #     managers_clients = manager.clients if manager else []
        #     return jsonify(
        #         data=clients_schema.dump(managers_clients).data
        #     )
        # else:
        #     return abort(404, "No clients for current user.")
