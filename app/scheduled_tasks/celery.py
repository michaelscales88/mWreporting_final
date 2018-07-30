# config/celery.py
from celery import Celery


def create_celery(app_instance):
    celery = Celery(
        app_instance.import_name,
        broker=app_instance.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app_instance.config)

    class ContextTask(celery.Task):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app_instance.app_context():
                return super().__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery
