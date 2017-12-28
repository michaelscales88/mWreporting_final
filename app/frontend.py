# app/frontend.py
from datetime import datetime, timedelta
from flask import Blueprint, abort, render_template


from app.util.tasks import get_model_headers


frontend_bp = Blueprint(
    'frontend', __name__
)


@frontend_bp.route('/', defaults={'page': 'index.html'})
@frontend_bp.route('/<string:page>')
def serve_pages(page):
    if page in ("index.html", "index"):
        return render_template(
            'index.html',
            title='Home'
        )
    elif page in ("sla_report.html", "sla_report"):
        return render_template(
            'reportDisplay.html',
            title='Reports',
            api='reportapi',
            columns=get_model_headers('sla_report'),
            start_date=None,
            end_date=None
        )
    elif page in ("data.html", "data"):
        date_time = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        print(date_time)
        return render_template(
            'dataDisplay.html',
            title='Data',
            api='dataapi',
            columns=get_model_headers('c_call'),
            end_date=date_time.isoformat(' '),
            start_date=(date_time - timedelta(days=1)).isoformat(' ')
        )
    elif page in ("clients.html", "clients"):
        return render_template(
            'clients.html',
            title='Clients',
            api='clientapi',
            columns=get_model_headers('client_table'),
            start_date=None,
            end_date=None
        )
    else:
        return abort(404)
