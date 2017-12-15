from flask_nav import Nav
from flask_nav.elements import Navbar, View


def get_nav(app):
    nav = Nav(app)
    nav.register_element(
        'main_nav', Navbar(
            View('Home', 'index')
        )
    )
    return nav
