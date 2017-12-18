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