# app/frontend.py
from datetime import datetime, timedelta
from flask import Blueprint, abort, render_template

from app.util.tasks import display_columns

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
            'report/reportDisplay.html',
            title='Reports',
            api='backend.report',
            columns=display_columns('sla_report'),
            end_time=zero_hour.isoformat(' '),
            start_time=(zero_hour - timedelta(days=1)).isoformat(' '),
            grid_length=50,
            client_api="backend.client"
        )
    elif page in ("data.html", "data"):
        return render_template(
            'data/dataDisplay.html',
            title='Data',
            api='backend.data',
            client_api='backend.client',
            columns=display_columns('c_call'),
            end_time=zero_hour.isoformat(' '),
            start_time=(zero_hour - timedelta(days=1)).isoformat(' '),
            grid_length=50
        )
    elif page in ("clientDisplay.html", "client"):
        return render_template(
            'client/clientDisplay.html',
            title='Clients',
            api='backend.client',
            columns=display_columns('client_table'),
            grid_length=50
        )
    else:
        return abort(404)
