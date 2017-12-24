from flask import Blueprint, abort, render_template, current_app


from app.data.tasks import get_model_headers
from .tasks import get_report_headers


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
    if page in ("report.html", "report"):
        return render_template(
            'report.html',
            title='Reports',
            iDisplayLength=current_app.config['ROWS_PER_PAGE'],
            api='reportapi',
            columns=get_report_headers('sla_report'),
            start_date=None,
            end_date=None
        )
    elif page in ("data.html", "data"):
        return render_template(
            'report.html',
            title='Data',
            iDisplayLength=current_app.config['ROWS_PER_PAGE'],
            api='dataapi',
            columns=get_model_headers('loc_call'),
            start_date=None,
            end_date=None
        )
    else:
        return abort(404)
