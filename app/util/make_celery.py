from celery import Celery
from kombu.serialization import register
from .json_encoder import my_loads, my_dumps

# Set the JSON encoder for Celery
register(
    'myjson',
    my_dumps,
    my_loads,
    content_type='application/x-myjson',
    content_encoding='utf-8'
)


def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL'],
        backend=app.config['CELERY_RESULT_BACKEND']
    )
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery
