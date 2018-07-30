# celery.py
from .tasks import create_celery
from app import app_instance

celery = create_celery(app_instance)
