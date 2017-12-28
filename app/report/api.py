# report/api.py
from flask import jsonify, g
from flask_restful import Resource


from .tasks import report_task


class Report(Resource):

    def get(self):
        print('Hit GET Report API')
        args = g.parser.parse_args()
        print(args)
        frame, status, tb = report_task(
            args['task'],
            start_time=args['start_time'],
            end_time=args['end_time']
        )
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
        print('Hit PUT Report API')
        args = g.parser.parse_args()
        print(args)
        result, status, tb = report_task(
            args['task'],
            start_time=args['start_time'],
            end_time=args['end_time']
        )
        print('did a task')
        return jsonify(
            status=status,
        )
