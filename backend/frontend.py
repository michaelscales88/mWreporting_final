# backend/frontend.py
from datetime import datetime, timedelta
from flask import Blueprint, abort, render_template

from backend.services.app_tasks import display_columns

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
            'report.html',
            title='Reports',
            api='backend.slareportapi',
            columns=display_columns('sla_report'),
            grid_length=50,
            client_api="backend.clientapi",
            task="sla_report"
        )
    elif page in ("data.html", "data"):
        return render_template(
            'data.html',
            title='Data',
            api='backend.dataapi',
            data_api='backend.clientapi',
            columns=display_columns('c_call'),
            grid_length=50,
            task="get"
        )
    elif page in ("clientDisplay.html", "client"):
        return render_template(
            'client.html',
            title='Clients',
            api='backend.clientapi',
            columns=display_columns('client_table'),
            grid_length=50,
            task="get"
        )
    else:
        return abort(404)
