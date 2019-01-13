from modules.celery_worker import celery
from dateutil.parser import parse
from .getters import *
from .loaders import *


@celery.task(bind=True, max_retries=10)
def call_data_task(self, *args, **kwargs):
    logger.warning("Starting call data task.")
    logger.warning("Received arguments [ {} ]".format(
        ",".join(["{}: {}".format(k, v) for k, v in kwargs.items()]))
    )
    load_date = parse(kwargs.pop("load_date")).date()
    try:
        service_result = call_data_loader(load_date)
        if not service_result:
            raise AssertionError("Retry")
    except Exception as err:
        logger.warning(err)
        self.retry(countdown=2 ** self.request.retries)


@celery.task(bind=True, max_retries=10, rate_limit='6/m')
def event_data_task(self, *args, **kwargs):
    logger.warning("Starting event data task.")
    logger.warning("Received arguments [ {} ]".format(
        ",".join(["{}: {}".format(k, v) for k, v in kwargs.items()]))
    )
    load_date = parse(kwargs.pop("load_date")).date()
    try:
        service_result = event_data_loader(load_date)
        if not service_result:
            raise AssertionError("Retry")
    except Exception as err:
        logger.warning(err)
        self.retry(countdown=2 ** self.request.retries)


@celery.task(bind=True, max_retries=10)
def report_task(self, *args, **kwargs):
    logger.warning("Starting report data task.")
    logger.warning("Received arguments [ {} ]".format(
        ",".join(["{}: {}".format(k, v) for k, v in kwargs.items()]))
    )
    start_time = parse(kwargs.pop("start_time"))
    end_time = parse(kwargs.pop("end_time"))
    try:
        service_result = report_loader(start_time, end_time)
        if not service_result:
            raise AssertionError("Retry")
    except Exception as err:
        logger.warning(err)
        self.retry(countdown=2 ** self.request.retries)
