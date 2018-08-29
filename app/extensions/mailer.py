# config/mailer.py
import logging
from flask import current_app
from . import mail
from .flask_mail import FlaskMailHandler
from app.celery_tasks import celery


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


class AsyncFlaskMailer(FlaskMailHandler):

    @staticmethod
    @celery.task(name="extensions.mailer.send_async_email")
    def send_async_email(msg):
        """Background task to send an email with Flask-Mail."""
        mail.send(msg)

    def handle(self, record):
        """
        Conditionally emit the specified logging record.

        Emission depends on filters which may have been added to the handler.
        Wrap the actual emission of the record with acquisition/release of
        the I/O thread lock. Returns whether the filter passed the record for
        emission.
        """
        rv = self.filter(record)
        if rv:
            self.acquire()
            try:
                self.emit(record)
            finally:
                self.release()
        return rv


def init_notifications():
    mail_handler = FlaskMailHandler(mail, subject_template)
    mail_handler.setLevel(logging.ERROR)
    mail_handler.setFormatter(text_template, html_template)
    current_app.logger.addHandler(mail_handler)
