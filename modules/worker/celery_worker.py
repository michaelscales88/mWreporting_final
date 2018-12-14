from celery import Celery


def get_celery(app):
    celery = Celery(__name__, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return super().__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery
