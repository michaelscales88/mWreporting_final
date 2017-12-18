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


@celery.task
def fetch_report(start_date, end_date, report_id=None):
    """
    Get report from id if it exists or make the report for the interval
    """
    # Add report model stuff here
    print('for sure i did this')
    return {
        'test': 'Test Successful',
        'start_date': start_date,
        'end_date': end_date,
        'report_id': report_id
    }


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
