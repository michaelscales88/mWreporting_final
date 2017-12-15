from app import celery, mail


@celery.task
def test(arg):
    print(arg)
    return arg


@celery.task
def send_async_email(msg):
    """Background task to send an email with Flask-Mail."""
    # mail.send(msg)
