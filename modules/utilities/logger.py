import logging
import os
from copy import copy
from logging.handlers import TimedRotatingFileHandler

from flask import current_app


def set_logger(level, name='app', rotating=True):
    logger = logging.getLogger(name)

    if rotating:
        file_handler = get_rotating_handler(name)
    else:
        file_handler = get_persistent_handler(name)

    for handler in copy(logger.handlers):
        logging.getLogger(name).removeHandler(handler)
        handler.close()  # clean up used file handles

    logger.setLevel(level)
    logger.addHandler(file_handler)


def get_formatter():
    return logging.Formatter(
        "[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s"
    )


def get_log_dir(log_name):
    log_dir = os.path.join(current_app.config["LOGS_DIR"], log_name)
    os.makedirs(log_dir, exist_ok=True)
    return log_dir


def get_rotating_handler(log_name):
    log_file_path = os.path.join(
        get_log_dir(log_name), "{name}.log".format(name=log_name)
    )
    file_handler = TimedRotatingFileHandler(
        filename=log_file_path,
        when='midnight',
        backupCount=45
    )
    file_handler.setFormatter(get_formatter())
    return file_handler


def get_persistent_handler(log_name):
    log_file_path = os.path.join(
        get_log_dir(log_name), "{name}.log".format(name=log_name)
    )
    file_handler = logging.FileHandler(filename=log_file_path)
    file_handler.setFormatter(get_formatter())
    return file_handler
