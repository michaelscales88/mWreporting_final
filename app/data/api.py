from flask import jsonify
from flask_restful import Resource
from flask_restful.reqparse import RequestParser


from .tasks import data_task


class DataApi(Resource):

    def get(self):
        print('Hit GET Data API')
        parser = RequestParser()
        parser.add_argument('start', type=int, location='args')
        parser.add_argument('draw', type=int, location='args')
        parser.add_argument('length', type=int, location='args')
        args = parser.parse_args()

        from datetime import datetime, timedelta
        today = datetime.today().now()
        result, status, tb = data_task('get_test', today - timedelta(hours=8), today - timedelta(hours=3))
        # frame, total = server_side_processing(result, args, model_name='loc_call')
        # data = frame.to_dict(orient='split')
        total = 100
        data = {'data': []}
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

    def put(self):
        print('Hit PUT Data API')
        parser = RequestParser()
        args = parser.parse_args()
        from datetime import datetime, timedelta
        today = datetime.today().now()
        result, status, tb = data_task('load_test', today - timedelta(hours=8), today - timedelta(hours=3))
        print('did a task')
        if isinstance(result, Exception):
            return jsonify(
                {
                    'status': status,
                    'error': str(result),
                    'traceback': tb,
                }
            )
        return jsonify(
            status=status,
            result=result,
        )
