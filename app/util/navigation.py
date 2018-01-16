from flask_nav import Nav
from flask_nav.elements import Navbar, View, Subgroup, Separator


def get_nav(app):
    nav = Nav(app)
    nav.register_element('main_nav', Navbar(
            View('Home', 'frontend.serve_pages', page='index'),
            Subgroup(
                'Reports',
                View('SLA Report', 'frontend.serve_pages', page='sla_report'),
                View('Data', 'frontend.serve_pages', page='data'),
                Separator(),
                View('Clients', 'frontend.serve_pages', page='client'),
            ),
        )
    )
    return nav
