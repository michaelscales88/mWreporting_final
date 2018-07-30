# scheduled_tasks/__init__.py
from flask import Blueprint
from flask_restful import Api


from app import app_instance, admin, db
from .celery import create_celery
from .views import ScheduledItemsView


scheduled_tasks_bp = Blueprint('tasks_bp', __name__)
scheduled_tasks_api = Api(scheduled_tasks_bp)


""" Create models for module in dB """
with app_instance.app_context():
    from app.scheduled_tasks.models.models import ScheduleItemModel
    # Creates any models that have been imported
    db.create_all()

    # Register the admin views to the extension
    admin.add_view(ScheduledItemsView(ScheduleItemModel, db.session, name='Scheduled Reports'))


app_instance.register_blueprint(scheduled_tasks_bp)
