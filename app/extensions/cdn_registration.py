# services/app_cdns.py
from flask_bootstrap import WebCDN


def register_app_cdn(app):
    # Date and Time selector
    app.extensions['bootstrap']['cdns']['bootstrapdtp'] = WebCDN(
        'https://cdnjs.cloudflare.com/ajax/libs/bootstrap-datetimepicker/4.17.47/'
    )
    # DataTable for displaying information in a grid
    app.extensions['bootstrap']['cdns']['dataTable'] = WebCDN(
        'https://cdn.datatables.net/1.10.16/'
    )
    # Buttons for saving/printing
    app.extensions['bootstrap']['cdns']['dataTableBtns'] = WebCDN(
        'https://cdn.datatables.net/buttons/1.5.1/'
    )
    app.extensions['bootstrap']['cdns']['saveJs'] = WebCDN(
        'https://cdnjs.cloudflare.com/ajax/libs/'
    )
    app.extensions['bootstrap']['cdns']['multiselect'] = WebCDN(
        'https://cdnjs.cloudflare.com/ajax/libs/bootstrap-select/1.12.4/'
    )
    app.extensions['bootstrap']['cdns']['toastr'] = WebCDN(
        'https://cdnjs.cloudflare.com/ajax/libs/toastr.js/'
    )



