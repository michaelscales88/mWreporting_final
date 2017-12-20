from flask import jsonify
from flask_restful import Resource
from flask_restful.reqparse import RequestParser

from .tasks import get_data


class DataApi(Resource):

    def get(self):
        print('Hit Data API')
        parser = RequestParser()
        args = parser.parse_args()
        async_result = get_data.delay('Today', 'Yesterday', 1)
        try:
            result = get_data.get(timeout=5, propagate=False)
        except TimeoutError:
            result = None
        status = get_data.status
        traceback = get_data.traceback
        data = []
        if isinstance(result, Exception):
            return jsonify(
                {
                    'status': status,
                    'error': str(result),
                    'traceback': traceback,
                }
            )
        else:
            return jsonify(
                status=status,
                result=result,
            )
