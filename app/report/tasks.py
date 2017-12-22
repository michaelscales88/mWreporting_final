from app import celery

from .models import SLAReport


_mmap = {
    "sla_report": SLAReport
}


def get_report_headers(model=None):
    if model in _mmap.keys():
        return _mmap.get(model, None).__repr_attrs__
    return None


def test_report(start_date, end_date, report_id=None):
    """
    Get report from id if it exists or make the report for the interval
    """
    # Add report model stuff here
    print('for sure i did this')
    return [{
        'id': 'Test Successful',
        'date': start_date,
        'report': end_date,
        'notes': report_id
    }], None, 200


@celery.task
def fetch_report(start_date, end_date, report_id=None):
    """
    Get report from id if it exists or make the report for the interval
    """
    # Add report model stuff here
    print('for sure i did this')
    return [{
        'id': 'Test Successful',
        'date': start_date,
        'report': end_date,
        'notes': report_id
    }]
