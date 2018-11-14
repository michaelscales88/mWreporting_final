from . import app
from .celery_tasks import create_celery

with app.app_context():
    celery = create_celery(app)
