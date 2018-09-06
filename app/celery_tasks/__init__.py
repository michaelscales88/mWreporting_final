# scheduled_tasks/__init__.py
from flask import Blueprint
from flask_restful import Api
from celery import Celery
from celery.utils.log import get_task_logger

from app import app_instance, admin, db
from .views import ScheduleDispatchItemView


scheduled_tasks_bp = Blueprint('tasks_bp', __name__)
scheduled_tasks_api = Api(scheduled_tasks_bp)

task_logger = get_task_logger(__name__)


def create_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return super().__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery


""" Create models for module in dB """
with app_instance.app_context():
    from .models import ScheduleDispatchItemModel
    # Creates any models that have been imported
    db.create_all()

    # Register the admin views to the extension
    admin.add_view(ScheduleDispatchItemView(ScheduleDispatchItemModel, db.session, name='Scheduled Tasks'))


app_instance.register_blueprint(scheduled_tasks_bp)
