# services/flask_nav.py
from flask_nav import Nav
from flask_nav.elements import Navbar, View, Subgroup


def get_nav():
    nav = Nav()
    nav.register_element(
        'main_nav', Navbar(
            View('Home', 'frontend.serve_pages', page='index'),
            Subgroup(
                'Reports',
                View('SLA Report', 'frontend.serve_pages', page='sla_report'),
                View('Data', 'frontend.serve_pages', page='data'),
            ),
            Subgroup(
                'Clients',
                View('Clients', 'frontend.serve_pages', page='client'),
            )
        )
    )
    return nav
