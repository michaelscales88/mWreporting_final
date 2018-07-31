# celery.py
from sqlalchemy.exc import DatabaseError

from app import app_instance
from app.extensions import BaseModel
from .scheduled_tasks import create_celery

celery = create_celery(app_instance)


class SqlAlchemyTask(celery.Task):
    """An abstract Celery Task that ensures that the connection the the
    database is closed on task completion"""
    abstract = True

    def __call__(self, *args, **kwargs):
        try:
            return super().__call__(*args, **kwargs)
        except DatabaseError:
            BaseModel.session.rollback()
        finally:
            BaseModel.session.commit()
