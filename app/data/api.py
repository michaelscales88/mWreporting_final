from flask import jsonify
from flask_restful import Resource
from flask_restful.reqparse import RequestParser

from .tasks import data_task


class DataApi(Resource):

    def get(self):
        print('Hit Data API')
        parser = RequestParser()
        args = parser.parse_args()
        print('starting a task')
        result, status, tb = data_task('load_test', 'Today', 'Yesterday')
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
