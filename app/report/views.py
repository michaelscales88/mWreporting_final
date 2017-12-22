from flask import Blueprint, abort, render_template, jsonify, current_app
from flask_restful import Resource
from flask_restful.reqparse import RequestParser


from app.data.tasks import get_model_headers
from app.util.server_processing import server_side_processing


from .tasks import test_report, fetch_report, get_report_headers


report_blueprint = Blueprint(
    'report', __name__,
    template_folder='pages',
    static_folder='static',
    static_url_path='/report/static'
)
_BASE_URL = '/report'


@report_blueprint.route(_BASE_URL, defaults={'page': 'report.html'})
@report_blueprint.route(_BASE_URL + '/', defaults={'page': 'report.html'})
@report_blueprint.route(_BASE_URL + '/<page>')
def serve_pages(page):
    if page == "report.html":
        return render_template(
            'report.html',
            title='Reports',
            iDisplayLength=current_app.config['ROWS_PER_PAGE'],
            api='reportapi',
            columns=get_report_headers('sla_report')
        )
    elif page == "data.html":
        return render_template(
            'report.html',
            title='Data',
            iDisplayLength=current_app.config['ROWS_PER_PAGE'],
            api='dataapi',
            columns=get_model_headers('loc_call')
        )
    else:
        return abort(404)


class ReportApi(Resource):

    def get(self):
        from datetime import datetime, timedelta
        today = datetime.today().now()

        print('Hit API')
        parser = RequestParser()
        parser.add_argument('start', type=int, location='args')
        parser.add_argument('draw', type=int, location='args')
        parser.add_argument('length', type=int, location='args')
        args = parser.parse_args()

        result, status, tb = test_report('get_test', today - timedelta(hours=8), today - timedelta(hours=3))
        frame, total = server_side_processing(result, args, model_name='loc_call')
        data = frame.to_dict(orient='split')
        if isinstance(result, Exception):
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
                draw=args['draw'],
                recordsTotal=total,
                recordsFiltered=total,
                data=data['data']
            )
