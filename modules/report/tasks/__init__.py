from modules.worker.celery_worker import celery
from .getters import *
from .loaders import *


@celery.task(bind=True, max_retries=10)
def call_data_task(self, *args, **kwargs):
    logger.warning("Starting call data task.")
    load_date = kwargs.pop("load_date")
    try:
        service_result = call_data_loader(load_date)
        if not service_result:
            raise AssertionError("Retry")
    except Exception as err:
        logger.warning(err)
        self.retry(countdown=2 ** self.request.retries)


@celery.task(bind=True, max_retries=10)
def event_data_task(self, *args, **kwargs):
    logger.warning("Starting event data task.")
    load_date = kwargs.pop("load_date")
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
    start_time = kwargs.pop("start_time")
    end_time = kwargs.pop("end_time")
    try:
        service_result = event_data_loader(start_time, end_time)
        if not service_result:
            raise AssertionError("Retry")
    except Exception as err:
        logger.warning(err)
        self.retry(countdown=2 ** self.request.retries)
