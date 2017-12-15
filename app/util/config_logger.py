import logging
from logging.handlers import RotatingFileHandler


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
