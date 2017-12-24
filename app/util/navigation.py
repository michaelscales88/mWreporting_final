from flask_nav import Nav
from flask_nav.elements import Navbar, View, Subgroup, Separator


def get_nav(app):
    nav = Nav(app)
    nav.register_element(
        'main_nav', Navbar(
            View('Home', 'index'),
            Subgroup(
                'Reports',
                View('SLA Report', 'report.serve_pages', page='report'),
                View('Data', 'report.serve_pages', page='data'),
                Separator(),
                View('Clients', 'report.serve_pages', page='client'),
            )
        )
    )
    return nav
