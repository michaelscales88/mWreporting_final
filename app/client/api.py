from flask import jsonify
from flask_restful import Resource
from flask_restful.reqparse import RequestParser


from app.util.server_processing import query_to_frame
from .tasks import get_clients


class ClientApi(Resource):

    def get(self):
        print('Hit GET Data API')
        parser = RequestParser()
        args = parser.parse_args()

        query = get_clients()
        frame = query_to_frame(query)
        data = frame.to_dict(orient='split')
        status = 200
        tb = 'Test'

        if isinstance(query, Exception):
            return jsonify(
                {
                    'status': status,
                    'error': str(frame),
                    'traceback': tb,
                }
            )
        else:
            return jsonify(
                status=status,
                draw=args['draw'],
                recordsTotal=len(frame.index),
                recordsFiltered=len(frame.index),
                data=data['data']
            )
