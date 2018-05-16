# backend/frontend.py
from flask import Blueprint, abort, render_template, redirect, url_for
from flask_user import login_required

from backend.services.app_tasks import display_columns

frontend_bp = Blueprint(
    'frontend', __name__
)


@frontend_bp.route('/')
def default():
    return redirect(url_for("frontend.serve_pages", page="index"))


@frontend_bp.route('/<string:page>')
def serve_pages(page):
    if page in ("index.html", "index"):
        return render_template(
            'index.html',
            title='Home'
        )
    elif page in ("sla_report.html", "sla_report"):
        return render_template(
            'sla_report.html',
            title='Reports',
            columns=display_columns('sla_report')
        )
    elif page in ("data.html", "data"):
        return render_template(
            'data.html',
            title='Data',
            columns=display_columns('c_call')
        )
    elif page in ("client.html", "client"):
        return restricted_page(
            'client.html',
            title='Clients',
            columns=display_columns('client_table')
        )
    elif page in ("user.html", "user"):
        return restricted_page(
            'user.html',
            title='User Page'
        )
    else:
        return abort(404)


@login_required
def restricted_page(*args, **kwargs):
    return render_template(
        *args, **kwargs
    )
