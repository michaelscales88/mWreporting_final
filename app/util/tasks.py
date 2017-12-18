from kombu import serialization

from app import celery, mail


@celery.task
def test(arg):
    print(arg)
    return arg


@celery.task
def send_async_email(msg):
    """Background task to send an email with Flask-Mail."""
    mail.send(msg)


def serialization_register_json():
    """Register a encoder/decoder for JSON serialization."""

    from anyjson import loads as json_loads, dumps as json_dumps

    def _loads(obj):
        if isinstance(obj, serialization.bytes_t):
            obj = obj.decode()
        # Make this the custom loader
        obj = json_loads(obj)
        if hasattr(obj, 'get') and obj.get('traceback') is not None:
            try:
                exc_type = obj['result']['exc_type']
                exc_message = obj['result']['exc_message']
            except KeyError:
                pass
            else:
                exc_type = getattr(obj, exc_type)
                obj['result'] = exc_type(exc_message)
        return obj

    serialization.registry.register('json', json_dumps, _loads,
                                    content_type='application/json',
                                    content_encoding='utf-8')
