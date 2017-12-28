# data/api.py
from datetime import datetime as dt
from flask import jsonify
from flask_restful import Resource
from flask_restful.reqparse import RequestParser


from .tasks import data_task


class DataApi(Resource):

    def get(self):
        print('Hit GET Data API')
        parser = RequestParser()
        parser.add_argument('start_time', type=str, location='args')
        parser.add_argument('end_time', type=str, location='args')
        args = parser.parse_args()
        print(args)
        from datetime import datetime, timedelta
        today = datetime.today().now()
        frame, status, tb = data_task('get', start_time=today - timedelta(hours=8), end_time=today - timedelta(hours=3))
        data = frame.to_dict(orient='split')
        if isinstance(data, Exception):
            return jsonify(
                {
                    'status': status,
                    'error': str(status),
                    'traceback': tb,
                }
            )
        else:
            return jsonify(
                status=status,
                recordsTotal=len(frame.index),
                recordsFiltered=len(frame.index),
                data=data['data']
            )

    def put(self):
        print('Hit PUT Data API')
        parser = RequestParser()
        parser.add_argument('client_name')
        parser.add_argument('client_ext')
        parser.add_argument('task')
        args = parser.parse_args()
        print(args)
        from datetime import datetime, timedelta
        today = datetime.today().now()
        result, status, tb = data_task(
            args['task'],
            start_time=today - timedelta(hours=4, minutes=30),
            end_time=today - timedelta(hours=3)
        )
        print('did a task')
        return jsonify(
            status=status,
        )
