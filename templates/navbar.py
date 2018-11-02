# services/flask_nav.py
from flask import current_app
from flask_nav import Nav
from flask_nav.elements import Navbar, View, Subgroup
from flask_security import current_user


def mynavbar():
    return Navbar(
        current_app.config.get('SITE_NAME'),
        View('Home', 'frontend_bp.serve_pages', page='index'),
        Subgroup(
            'Reports',
            View('Daily Report', 'frontend_bp.serve_pages', page='dailyl-report'),
            View('Summary Report', 'frontend_bp.serve_pages', page='summary-report'),
        )
    )


def secnavbar():
    secnav = list(mynavbar().items)
    if current_user.is_authenticated:
        secnav.extend([
            Subgroup(
                'Admin',
                View('Admin Page', 'admin.index')
            ),
            View('Log out', 'logout')
        ])
    else:
        secnav.extend([
            View('Log in', 'admin.index')
        ])
    return Navbar(current_app.config.get('SITE_NAME'), *secnav)


def get_nav():
    nav = Nav()
    nav.register_element('mynavbar', mynavbar)
    nav.register_element('secnavbar', secnavbar)
    return nav
