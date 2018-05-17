# services/flask_nav.py
from flask_nav import Nav
from flask_nav.elements import Navbar, View, Subgroup
from flask_user import current_user, current_app


def mynavbar():
    return Navbar(
        current_app.config.get('SITE_NAME'),
        View('Home', 'frontend.serve_pages', page='index'),
        Subgroup(
            'Reports',
            View('SLA Report', 'frontend.serve_pages', page='sla_report'),
            View('Data', 'frontend.serve_pages', page='data'),
        )
    )


def secnavbar():
    secnav = list(mynavbar().items)
    if current_user.is_authenticated:
        secnav.extend([
            Subgroup(
                'Clients',
                View('Clients', 'frontend.serve_pages', page='client'),
            ),
            Subgroup(
                'User',
                View('User', 'frontend.serve_pages', page='user'),
            ),
            View('Log out', 'logout')
        ])
    else:
        secnav.extend([
            View('Log in', 'user.login')
        ])
    return Navbar(current_app.config.get('SITE_NAME'), *secnav)


def get_nav():
    nav = Nav()
    nav.register_element('mynavbar', mynavbar)
    nav.register_element('secnavbar', secnavbar)
    return nav
