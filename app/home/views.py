# app/home/views.py
from flask import Blueprint, abort


home_blueprint = Blueprint('home', __name__)
_BASE_URL = '/home'


@home_blueprint.route(_BASE_URL, defaults={'page': 'index.html'})
@home_blueprint.route(_BASE_URL + '/', defaults={'page': 'index.html'})
@home_blueprint.route(_BASE_URL + '/<page>')
def serve_pages(page):
    if page == "index.html":
        return 'Working'
    else:
        return abort(404)
