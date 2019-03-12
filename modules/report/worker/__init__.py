from modules.celery_worker import celery
from dateutil.parser import parse
from .getters import *
from .loaders import *


def log_kwargs(kwargs):
    logger.warning("Received arguments [ {} ]".format(
        ", ".join(["{}: {}".format(k, v) for k, v in kwargs.items()]))
    )


@celery.task(bind=True, max_retries=10)
def load_call_data_task(self, *args, **kwargs):
    """
    rate_limit: unlimited since the limited is the source
    :param self:
    :param args:
    :param kwargs:
    :return:
    """
    logger.warning("Starting call data task.")
    log_kwargs(kwargs)
    load_date = parse(kwargs.pop("load_date")).date()
    with_events = kwargs.pop("with_events")
    session = get_session(current_app)[1]
    try:
        service_result = call_data_loader(load_date)
        if not service_result:
            raise AssertionError("Retry")
    except Exception as err:
        logger.warning(err)
        self.retry(countdown=2 ** self.request.retries)
    except DatabaseError:
        logger.error("Error committing event records to target database.")
        session.rollback()
    else:
        if with_events:
            load_event_data_task.delay(load_date=load_date)
    finally:
        session.close()


@celery.task(bind=True, max_retries=10, rate_limit='6/m')
def load_event_data_task(self, *args, **kwargs):
    """
    rate_limit: 1 every 10 seconds to prevent duplication
    :param self:
    :param args:
    :param kwargs:
    :return:
    """
    logger.warning("Starting event data task.")
    log_kwargs(kwargs)
    load_date = parse(kwargs.pop("load_date")).date()
    session = get_session(current_app)[1]
    try:
        service_result = event_data_loader(load_date)
        if not service_result:
            raise AssertionError("Retry")
    except Exception as err:
        logger.warning(err)
        self.retry(countdown=2 ** self.request.retries)
    except DatabaseError:
        logger.error("Error committing event records to target database.")
        session.rollback()
    finally:
        session.close()


@celery.task(bind=True, max_retries=10, rate_limit='3/m')
def load_report_task(self, *args, **kwargs):
    """
    rate_limit: 3 per minutes to prevent bottlenecking
    :param self: references to remember # retries
    :param args: None
    :param kwargs:
    :return:
    """
    logger.warning("Starting report task.")
    log_kwargs(kwargs)
    start_time = parse(kwargs.pop("start_time"))
    end_time = parse(kwargs.pop("end_time"))
    session = get_session(current_app)[1]
    try:
        service_result = report_loader(start_time, end_time, session)
        if not service_result:
            raise AssertionError("Retry")
        if service_result == "delay":
            raise AssertionError("Delay")
    except AssertionError as err:
        logger.warning(err)
        is_delay = isinstance(err, type(AssertionError("Delay")))
        self.retry(countdown=30 if is_delay else (2 ** self.request.retries))
    except DatabaseError:
        logger.error("Error committing event records to target database.")
        session.rollback()
    finally:
        session.close()


@celery.task
def remove_data(*args, **kwargs):
    """
    Want to remove data when the TableLoadedModel is removed
    :param args: date to remove
    :param kwargs:
    :return:
    """
    logger.warning("Removing data from local database.")
    log_kwargs(kwargs)
    date_to_remove = parse(kwargs.pop("loaded_date"))
