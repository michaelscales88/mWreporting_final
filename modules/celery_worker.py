
from celery import Celery
from modules import app

with app.app_context():
    celery = Celery(__name__, broker=app.config['broker_url'])
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return super().__call__(self, *args, **kwargs)

    celery.Task = ContextTask
