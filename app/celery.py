# celery.py
from sqlalchemy.exc import DatabaseError
from celery.utils.log import get_task_logger

from app import app_instance
from app.extensions import BaseModel
from .scheduled_tasks import create_celery

app_instance.app_context().push()
celery = create_celery(app_instance)

logger = get_task_logger(__name__)


class SqlAlchemyTask(celery.Task):
    """An abstract Celery Task that ensures that the connection the the
    database is closed on task completion"""
    abstract = True

    def __call__(self, *args, **kwargs):
        try:
            logger.warning("Starting celery job.")
            return super().__call__(args[1:], **kwargs)
        except DatabaseError:
            BaseModel.session.rollback()
            logger.error("Leaving celery job on Database Error.")
        finally:
            BaseModel.session.commit()
            logger.warning("Leaving celery job on success.")
