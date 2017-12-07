from flask import render_template, g, current_app, url_for, redirect
from app import app


@app.route('/', methods=['GET', 'POST'])
def index():
    # User module is accessed through the navigation bar
    return "Hello World"
