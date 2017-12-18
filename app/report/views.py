from flask import Blueprint, abort, render_template, jsonify
from flask_restful import Resource
from app.util.tasks import fetch_report


report_blueprint = Blueprint(
    'report', __name__,
    template_folder='pages'
)
_BASE_URL = '/report'


@report_blueprint.route(_BASE_URL, defaults={'page': 'report.html'})
@report_blueprint.route(_BASE_URL + '/', defaults={'page': 'report.html'})
@report_blueprint.route(_BASE_URL + '/<page>')
def serve_pages(page):
    if page == "report.html":
        return render_template('report.html', title='Reports')
    else:
        return abort(404)


class ReportApi(Resource):

    def get(self):
        async_result = fetch_report.delay('Today', 'Yesterday', 1)
        try:
            result = async_result.get(timeout=5, propagate=False)
        except TimeoutError:
            result = None
        status = async_result.status
        traceback = async_result.traceback
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
                {
                    'status': status,
                    'result': result,
                }
            )