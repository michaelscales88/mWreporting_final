from flask_bootstrap import WebCDN


def add_cdns(app):
    app.extensions['bootstrap']['cdns']['bootstrapdtp'] = WebCDN(
        'https://cdnjs.cloudflare.com/ajax/libs/bootstrap-datetimepicker/4.17.47/'
    )
    app.extensions['bootstrap']['cdns']['dataTables'] = WebCDN(
        'https://cdn.datatables.net/1.10.16/'
    )



