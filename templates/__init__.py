# templates/frontend.py
from flask import Blueprint, abort, render_template, redirect, url_for

from .navbar import get_nav

# Export templates navbar
nav = get_nav()

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
    elif page in ("sla_report.html", "daily-report", "sla_report"):
        return render_template(
            'report/daily_report.html',
            title='Daily Report'
        )
    elif page in ("sla_summary_report.html", "summary-report", "summary_sla_report"):
        return render_template(
            'report/summary_report.html',
            title='Summary Report'
        )
    else:
        return abort(404)
