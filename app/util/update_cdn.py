from flask_bootstrap import WebCDN


def add_cdns(app):
    app.extensions['bootstrap']['cdns']['bootstrapdtp'] = WebCDN(
        'https://cdnjs.cloudflare.com/ajax/libs/bootstrap-datetimepicker/4.17.47/'
    )


