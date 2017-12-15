# app/home/views.py
from flask import Blueprint, abort, render_template

home_blueprint = Blueprint(
    'home', __name__,
    template_folder='templates'
)
_BASE_URL = '/home'


@home_blueprint.route(_BASE_URL, defaults={'page': 'index.html'})
@home_blueprint.route(_BASE_URL + '/', defaults={'page': 'index.html'})
@home_blueprint.route(_BASE_URL + '/<page>')
def serve_pages(page):
    if page == "index.html":
        return render_template('index.html', title='Home')
    else:
        return abort(404)
