from flask import Blueprint, abort, render_template, jsonify
from flask_restful import Resource


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
        return {'test': 'Test Successful'}
