# frontend/__init__.py
from flask import Blueprint, render_template, redirect, url_for

from .navbar import get_nav, register_nav_renderers

frontend_bp = Blueprint('frontend', __name__)


@frontend_bp.route('/favicon.ico')
def favicon():
    return redirect(url_for('static', filename='favicon.ico'), code=302)


@frontend_bp.route('/')
def no_endpoint_specified():
    return redirect(url_for("frontend.index"))


@frontend_bp.route("/report")
def index():
    return render_template(
        'report/index.html',
        title='Home'
    )


@frontend_bp.route("/report/sla-report")
def sla_report():
    return render_template(
        'report/daily_report.html',
        title='Daily Report'
    )


@frontend_bp.route("/report/summary-report")
def summary_report():
    return render_template(
        'report/summary_report.html',
        title='Summary Report'
    )
