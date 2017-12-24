from flask import jsonify, flash
from flask_restful import Resource
from flask_restful.reqparse import RequestParser


from app.util.tasks import query_to_frame
from .tasks import get_clients


class ClientApi(Resource):

    def get(self):
        print('Hit GET Client API')
        parser = RequestParser()
        args = parser.parse_args()

        query = get_clients()
        frame = query_to_frame(query)
        print(frame)
        data = frame.to_dict(orient='split')
        status = 200
        tb = 'Test'
        print(data)
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
                recordsTotal=len(frame.index),
                recordsFiltered=len(frame.index),
                data=data['data']
            )

    def post(self):
        print('hit POST Client API')
        flash('Added client!')
        parser = RequestParser()
        parser.add_argument('client_name')
        parser.add_argument('client_ext')
        args = parser.parse_args()
        print(args)
        status = 204
        return jsonify(
            status=status,
        )
