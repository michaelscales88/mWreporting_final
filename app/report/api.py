from flask import jsonify
from flask_restful import Resource
from flask_restful.reqparse import RequestParser


from app.util.server_processing import server_side_processing
from .tasks import test_report, fetch_report


class ReportApi(Resource):

    def get(self):
        from datetime import datetime, timedelta
        today = datetime.today().now()

        print('Hit API')
        parser = RequestParser()
        parser.add_argument('start', type=int, location='args')
        parser.add_argument('draw', type=int, location='args')
        parser.add_argument('length', type=int, location='args')
        args = parser.parse_args()

        result, status, tb = test_report('get_test', today - timedelta(hours=8), today - timedelta(hours=3))
        frame, total = server_side_processing(result, args, model_name='loc_call')
        data = frame.to_dict(orient='split')
        if isinstance(result, Exception):
            return jsonify(
                {
                    'status': status,
                    'error': str(result),
                    'traceback': tb,
                }
            )
        else:
            return jsonify(
                status=status,
                draw=args['draw'],
                recordsTotal=total,
                recordsFiltered=total,
                data=data['data']
            )
