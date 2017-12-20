from app import celery


@celery.task
def fetch_report(start_date, end_date, report_id=None):
    """
    Get report from id if it exists or make the report for the interval
    """
    # Add report model stuff here
    print('for sure i did this')
    return [{
        'test': 'Test Successful',
        'start_date': start_date,
        'end_date': end_date,
        'report_id': report_id
    }]
