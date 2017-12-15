import logging
from logging.handlers import RotatingFileHandler, SMTPHandler


def get_handler(log_filename):
    formatter = logging.Formatter(
        "[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
    handler = RotatingFileHandler(log_filename, maxBytes=10000000, backupCount=5)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    return handler


def get_logger(emitter):
    log = logging.getLogger(emitter)
    log.setLevel(logging.DEBUG)
    return log


def get_mail_handler(mailer):
    subject_template = 'Web-app problems in %(module)s > %(funcName)s'
    text_template = '''
    Message type: %(levelname)s
    Location:     %(pathname)s:%(lineno)d
    Module:       %(module)s
    Function:     %(funcName)s
    Time:         %(asctime)s
    Message:
    %(message)s'''
    html_template = '''
    <style>th { text-align: right}</style><table>
    <tr><th>Message type:</th><td>%(levelname)s</td></tr>
    <tr>    <th>Location:</th><td>%(pathname)s:%(lineno)d</td></tr>
    <tr>      <th>Module:</th><td>%(module)s</td></tr>
    <tr>    <th>Function:</th><td>%(funcName)s</td></tr>
    <tr>        <th>Time:</th><td>%(asctime)s</td></tr>
    </table>
    <h2>Message</h2>
    <pre>%(message)s</pre>'''

    import logging
    from .flask_mail import FlaskMailHandler
    mail_handler = FlaskMailHandler(mailer, subject_template)
    mail_handler.setLevel(logging.ERROR)
    mail_handler.setFormatter(text_template, html_template)
    return mail_handler
