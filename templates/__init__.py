# app/frontend.py
from flask import Blueprint, abort, render_template, redirect, url_for

from app.services.app_tasks import display_columns

frontend_bp = Blueprint('frontend_bp', __name__)


# Redirect app traffic to the modules default view
@frontend_bp.route('/')
def no_endpoint_specified():
    return redirect(url_for("frontend_bp.serve_pages", page="index"))


@frontend_bp.route('/<string:page>')
def serve_pages(page):
    if page in ("index.html", "index"):
        return render_template(
            'index.html',
            title='Home'
        )
    elif page in ("sla_report.html", "sla_report"):
        return render_template(
            'report/sla_report.html',
            title='SLA Report',
            columns=display_columns('sla_report')
        )
    else:
        return abort(404)
