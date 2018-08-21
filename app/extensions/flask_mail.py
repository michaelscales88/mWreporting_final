# services/app_mail.py
# Credit to Doekman https://gist.github.com/doekman/d24e233035c0a193d4890eaf9703e220
import logging
from flask_mail import Message


def _has_newline(line):
    """
    Used by has_bad_header to check for \\r or \\n
    """
    if line and ('\r' in line or '\n' in line):
        return True
    return False


def _is_bad_subject(subject):
    """
    Copied from: app_mail.py class Message def has_bad_headers
    """
    if _has_newline(subject):
        for linenum, line in enumerate(subject.split('\r\n')):
            if not line:
                return True
            if linenum > 0 and line[0] not in '\t ':
                return True
            if _has_newline(line):
                return True
            if len(line.strip()) == 0:
                return True
    return False


class FlaskMailSubjectFormatter(logging.Formatter):
    def format(self, record):
        record.message = record.getMessage()
        if self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)
        s = self.formatMessage(record)
        return s


class FlaskMailTextFormatter(logging.Formatter):
    pass


# TODO: hier nog niet tevreden over (vooral logger.error(..., exc_info, stack_info))
class FlaskMailHTMLFormatter(logging.Formatter):
    pre_template = '<h1>%s</h1><pre>%s</pre>'

    def formatException(self, exc_info):
        formatted_exception = logging.Handler.formatException(self, exc_info)
        return FlaskMailHTMLFormatter.pre_template % ('Exception information', formatted_exception)

    def formatStack(self, stack_info):
        return FlaskMailHTMLFormatter.pre_template % ('<h1>Stack information</h1><pre>%s</pre>', stack_info)


# see: https://github.com/python/cpython/blob/3.6/Lib/logging/__init__.py (class Handler)

class FlaskMailHandler(logging.Handler):
    def __init__(self, mailer, subject_template, level=logging.NOTSET):
        # Assumes mailer.app.conf[0] is the FROM: admin
        logging.Handler.__init__(self, level)
        self.mailer = mailer
        self.send_to = mailer.app.config['ADMINS']
        self.subject_template = subject_template
        self.html_formatter = None

    def setFormatter(self, text_fmt, html_fmt=None):
        """
        Set the formatters for this handler. Provide at least one formatter.
        When no text_fmt is provided, no text-part is created for the email body.
        """
        assert (text_fmt, html_fmt) != (None, None), 'At least one formatter should be provided'
        if type(text_fmt) == str:
            text_fmt = FlaskMailTextFormatter(text_fmt)
        self.formatter = text_fmt
        if type(html_fmt) == str:
            html_fmt = FlaskMailHTMLFormatter(html_fmt)
        self.html_formatter = html_fmt

    def get_subject(self, record):
        fmt = FlaskMailSubjectFormatter(self.subject_template)
        subject = fmt.format(record)

        # Since pages can cause header problems, and we rather
        # have a incomplete email then an error, we fix this
        if _is_bad_subject(subject):
            subject = 'FlaskMailHandler log-entry from %s [original subject is replaced, ' \
                      'because it would result in a bad header]' % self.mailer.app.name
        return subject

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

    def emit(self, record):
        try:
            msg = Message(self.get_subject(record), recipients=self.send_to, sender=self.send_to[0])
            if self.formatter:
                msg.body = self.format(record)
            if self.html_formatter:
                msg.html = self.html_formatter.format(record)
            self.mailer.send(msg)
        except Exception:
            self.handleError(record)
