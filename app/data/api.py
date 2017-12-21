from flask import jsonify
from flask_restful import Resource
from flask_restful.reqparse import RequestParser

from .tasks import data_task


class DataApi(Resource):

    def get(self):
        print('Hit GET Data API')
        parser = RequestParser()
        args = parser.parse_args()
        print('starting a task')
        from datetime import datetime, timedelta
        today = datetime.today().now()
        result, status, tb = data_task('get_test', today - timedelta(hours=8), today - timedelta(hours=3))
        print(result)
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
            result='Success',
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
