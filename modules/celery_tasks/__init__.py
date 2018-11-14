# scheduled_tasks/__init__.py
from flask import Blueprint
from flask_restful import Api
from celery.utils.log import get_task_logger

from modules import app, admin, db
from .views import ScheduleDispatchItemView


scheduled_tasks_bp = Blueprint('tasks_bp', __name__)
scheduled_tasks_api = Api(scheduled_tasks_bp)

task_logger = get_task_logger(__name__)


""" Create models for module in dB """
with app.app_context():
    from .models import ScheduleDispatchItemModel
    # Creates any models that have been imported
    db.create_all()

    # Register the admin views to the extension
    admin.add_view(ScheduleDispatchItemView(ScheduleDispatchItemModel, db.session, name='Scheduled Tasks'))


app.register_blueprint(scheduled_tasks_bp)
