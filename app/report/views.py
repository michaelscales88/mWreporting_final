from flask import Blueprint, abort, render_template, jsonify
from flask_restful import Resource
from flask_restful.reqparse import RequestParser


from .tasks import fetch_report


report_blueprint = Blueprint(
    'report', __name__,
    template_folder='pages',
    static_folder='static',
    static_url_path='/report/static'
)
_BASE_URL = '/report'
TEMP_HEADER_ORDER = ('report_id', 'end_date', 'start_date', 'test')


@report_blueprint.route(_BASE_URL, defaults={'page': 'report.html'})
@report_blueprint.route(_BASE_URL + '/', defaults={'page': 'report.html'})
@report_blueprint.route(_BASE_URL + '/<page>')
def serve_pages(page):
    if page == "report.html":
        return render_template(
            'report.html',
            title='Reports',
            iDisplayLength=50,
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

        async_result = fetch_report.delay('Today', 'Yesterday', 1)
        try:
            result = async_result.get(timeout=5, propagate=False)
        except TimeoutError:
            result = None
        status = async_result.status
        traceback = async_result.traceback
        data = []
        for r in result:
            data.append([r.get(header, '') for header in TEMP_HEADER_ORDER])
        print(data)
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
                draw=args['draw'],
                recordsTotal=1,
                recordsFiltered=1,
                data=data
            )
