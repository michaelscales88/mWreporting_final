from flask import jsonify
from flask_restful import Resource
from flask_restful.reqparse import RequestParser


from app.util.tasks import query_to_frame
from .tasks import get_reports


class Report(Resource):

    def get(self):
        print('Hit GET Report API')
        parser = RequestParser()
        args = parser.parse_args()

        query = get_reports()
        frame = query_to_frame(query)
        data = frame.to_dict(orient='split')

        status = 200
        result = 'test'
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
