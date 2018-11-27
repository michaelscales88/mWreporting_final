# scheduled_tasks/__init__.py
from flask import Blueprint
from flask_restful import Api
from celery.utils.log import get_task_logger

from modules import app
from modules.extensions import admin


scheduled_tasks_bp = Blueprint('tasks_bp', __name__)
scheduled_tasks_api = Api(scheduled_tasks_bp)

task_logger = get_task_logger(__name__)


""" Create models for module in dB """
with app.app_context():
    import modules.celery_tasks.views
    import modules.celery_tasks.models

    # Register the admin views to the extension
    admin.add_view(
        views.ScheduleDispatchItemView(
            models.ScheduleDispatchItemModel,
            models.ScheduleDispatchItemModel.session,
            name='Scheduled Tasks'
        )
    )


app.register_blueprint(scheduled_tasks_bp)
