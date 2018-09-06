from . import app_instance
from .celery_tasks import create_celery

with app_instance.app_context():
    celery = create_celery(app_instance)
