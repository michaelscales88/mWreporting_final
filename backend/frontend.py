# backend/frontend.py
from flask import Blueprint, abort, render_template

from backend.services.app_tasks import display_columns

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
            'report.html',
            title='Reports',
            api='backend.slareportapi',
            columns=display_columns('sla_report'),
            grid_length=50,
            task="sla_report",
            client_api="backend.clientapi",
        )
    elif page in ("data.html", "data"):
        return render_template(
            'data.html',
            title='Data',
            api='backend.dataapi',
            columns=display_columns('c_call'),
            grid_length=50,
            get_task="get",
            load_task="load"
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
