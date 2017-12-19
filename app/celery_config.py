import os


class Config(object):
    """
    Configure task queue
    """
    AMQP_USERNAME = os.getenv('AMQP_USERNAME', 'user')
    AMQP_PASSWORD = os.getenv('AMQP_PASSWORD', 'password')
    AMQP_HOST = os.getenv('AMQP_HOST', 'localhost')
    AMQP_PORT = int(os.getenv('AMQP_PORT', '5672'))

    DEFAULT_BROKER_URL = 'amqp://{user}:{pw}@{host}:{port}'.format(
        user=AMQP_USERNAME,
        pw=AMQP_PASSWORD,
        host=AMQP_HOST,
        port=AMQP_PORT
    )

    DEFAULT_CELERY_BACKEND = 'rpc://{user}:{pw}@{host}:{port}'.format(
        user=AMQP_USERNAME,
        pw=AMQP_PASSWORD,
        host=AMQP_HOST,
        port=AMQP_PORT
    )

    CELERY_BROKER_URL = os.getenv('BROKER_URL', DEFAULT_BROKER_URL)
    CELERY_RESULT_BACKEND = os.getenv('BACKEND_URL', DEFAULT_CELERY_BACKEND)

    CELERY_RESULT_SERIALIZER = 'json'

    CELERYBEAT_SCHEDULE_FILENAME = os.getenv(
        'CELERYBEAT_SCHEDULE_FILENAME', 'tmp/celerybeat-schedule'
    )

    IMPORTS = ('app.report.tasks', 'app.util.tasks')

    """
    Scheduler
    """
    CELERYBEAT_SCHEDULE = {}
