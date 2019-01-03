from modules.celery_worker import celery
from .getters import *
from .loaders import *


@celery.task(bind=True, max_retries=5)
def call_data_task(self, *args, **kwargs):
    logger.warning("Starting call data task.")
    load_date = datetime.datetime.strptime(
        kwargs.pop("load_date"), '%Y-%m-%dT%H:%M:%S'
    ).date()
    try:
        service_result = call_data_loader(load_date)
        if not service_result:
            raise AssertionError("Retry")
    except Exception as err:
        logger.warning(err)
        self.retry(countdown=2 ** self.request.retries)
    else:
        # Update the system that the interval is loaded
        tl_model = TablesLoadedModel.find(load_date)
        if load_date < utc_now().date():
            tl_model.update(calls_loaded=True)
            print("updated calls loaded")
        tl_model.update(last_updated=utc_now())
        tl_model.session.commit()
        tl_model.session.remove()


@celery.task(bind=True, max_retries=5)
def event_data_task(self, *args, **kwargs):
    logger.warning("Starting event data task.")
    load_date = datetime.datetime.strptime(
        kwargs.pop("load_date"), '%Y-%m-%dT%H:%M:%S'
    ).date()
    try:
        service_result = event_data_loader(load_date)
        if not service_result:
            raise AssertionError("Retry")
    except Exception as err:
        logger.warning(err)
        self.retry(countdown=2 ** self.request.retries)
    else:
        # Update the system that the interval is loaded
        tl_model = TablesLoadedModel.find(load_date)
        if load_date < utc_now().date():
            tl_model.update(events_loaded=True)
            print("updated events loaded")
        tl_model.update(last_updated=utc_now())
        tl_model.session.commit()
        tl_model.session.remove()


@celery.task(bind=True, max_retries=5)
def report_task(self, *args, **kwargs):
    logger.warning("Starting report data task.")
    start_time = datetime.datetime.strptime(
        kwargs.pop("start_time"), '%Y-%m-%dT%H:%M:%S'
    )
    end_time = datetime.datetime.strptime(
        kwargs.pop("end_time"), '%Y-%m-%dT%H:%M:%S'
    )
    try:
        service_result = report_loader(start_time, end_time)
        if not service_result:
            raise AssertionError("Retry")
    except Exception as err:
        logger.warning(err)
        self.retry(countdown=2 ** self.request.retries)
    else:
        # Update the system that the report is complete
        report = SlaReportModel.get(start_time, end_time)
        report.update(last_updated=utc_now())
        report.update(completed_on=utc_now())
        report.session.commit()
        report.session.remove()
