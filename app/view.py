from flask import render_template, g, current_app, url_for, redirect
from app import app


@app.route('/', methods=['GET', 'POST'])
def index():
    # User module is accessed through the navigation bar
    return redirect(
        url_for('index')
    )


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500
