from modules import app
from celery import Celery


# def create_celery(app_instance):
#
#
#     class ContextTask(celery.Task):
#         abstract = True
#
#         def __call__(self, *args, **kwargs):
#             with app_instance.app_context():
#                 return super().__call__(self, *args, **kwargs)
#
#     celery.Task = ContextTask
#     return celery


with app.app_context():
    celery = Celery(__name__, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
