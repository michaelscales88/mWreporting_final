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
    zero_hour = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    if page in ("index.html", "index"):
        return render_template(
            'index.html',
            title='Home'
        )
    elif page in ("sla_report.html", "sla_report"):
        return render_template(
            'data/dataDisplay.html',
            title='Reports',
            api='backend.report',
            columns=get_model_headers('sla_report'),
            end_time=zero_hour.isoformat(' '),
            start_time=(zero_hour - timedelta(days=1)).isoformat(' ')
        )
    elif page in ("data.html", "data"):
        return render_template(
            'data/dataDisplay.html',
            title='Data',
            api='backend.data',
            columns=get_model_headers('c_call'),
            end_time=zero_hour.isoformat(' '),
            start_time=(zero_hour - timedelta(days=1)).isoformat(' ')
        )
    elif page in ("clientsDisplay.html", "clients"):
        return render_template(
            'clients/clientsDisplay.html',
            title='Clients',
            api='backend.client',
            columns=get_model_headers('client_table'),
            start_date=None,
            end_date=None
        )
    else:
        return abort(404)
