# client/api.py
from flask import jsonify, flash, g
from flask_restful import Resource


from app.util.tasks import query_to_frame
from .tasks import client_task


class Client(Resource):

    def get(self):
        print('Hit GET Client API')
        args = g.parser.parse_args()

        query = client_task('get')
        frame = query_to_frame(query)
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

    def put(self):
        print('hit PUT Client API')
        # flash('Added client!')
        args = g.parser.parse_args()
        print(args)
        client_task(args['task'], args['client_name'], args['client_ext'])
        status = 204
        return jsonify(
            status=status,
        )
