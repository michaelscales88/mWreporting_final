from flask import jsonify
from flask_restful import Resource
from flask_restful.reqparse import RequestParser

from app.util.tasks import query_to_frame
from .tasks import get_records


class DataApi(Resource):

    def get(self):
        print('Hit GET Data API')
        parser = RequestParser()
        args = parser.parse_args()

        query = get_records()
        frame = query_to_frame(query)
        data = frame.to_dict(orient='split')

        status = 200
        result = 'ok'
        tb = 'good'

        if isinstance(query, Exception):
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
                recordsTotal=len(frame.index),
                recordsFiltered=len(frame.index),
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
