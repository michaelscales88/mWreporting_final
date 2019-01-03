# worker/__init__.py
from flask import Blueprint
from flask_restful import Api
from celery.utils.log import get_task_logger

from modules import app
from modules.extensions import admin


worker_bp = Blueprint('worker_bp', __name__)
worker_api = Api(worker_bp)

task_logger = get_task_logger(__name__)


""" Create models for module in dB """
with app.app_context():
    import modules.worker.views
    import modules.worker.models

    # Register the admin views to the extension
    admin.add_view(
        views.ScheduleDispatchItemView(
            models.ScheduleDispatchItemModel,
            models.ScheduleDispatchItemModel.session,
            name='Scheduled Tasks'
        )
    )


app.register_blueprint(worker_bp)
