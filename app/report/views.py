from flask import Blueprint, abort, render_template, jsonify, current_app
from flask_restful import Resource
from flask_restful.reqparse import RequestParser

from app.data.models import CallTable
from .tasks import fetch_report
from app.util import server_side_processing



report_blueprint = Blueprint(
    'report', __name__,
    template_folder='pages',
    static_folder='static',
    static_url_path='/report/static'
)
_BASE_URL = '/report'
# TEMP_HEADER_ORDER = ('report_id', 'end_date', 'start_date', 'test')
TEMP_HEADER_ORDER = CallTable.__table__.columns.keys()


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
            columns=TEMP_HEADER_ORDER
        )
    else:
        return abort(404)


class ReportApi(Resource):

    def get(self):
        print('Hit API')
        parser = RequestParser()
        parser.add_argument('start', type=int, location='args')
        parser.add_argument('draw', type=int, location='args')
        parser.add_argument('length', type=int, location='args')
        args = parser.parse_args()

        from app.data.tasks import data_task
        from datetime import datetime, timedelta
        today = datetime.today().now()
        result, status, tb = data_task('get_test', today - timedelta(hours=8), today - timedelta(hours=3))
        data = server_side_processing(result, args)
        results = data.to_dict(orient='split')
        data = results['data']
        print(data)
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
                recordsTotal=len(result.index),
                recordsFiltered=len(result.index),
                data=data
            )
