# report/tasks.py
import datetime

from .services import get_sla_report, empty_report
from celery.schedules import crontab


def register_tasks(server):
    end_time = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    start_time = end_time - datetime.timedelta(days=1)
    server.config['CELERYBEAT_SCHEDULE']['daily_report_task'] = {
        'task': 'app.report.services.sla_report.make_sla_report_model',
        'schedule': crontab(
            **{server.config['BEAT_PERIOD']: server.config['BEAT_RATE']}
        ),
        'args': (start_time, end_time,)
    }


def report_task(report_name, start_time=None, end_time=None, clients=None):
    if report_name == 'sla_report':
        if start_time and end_time:
            report = get_sla_report(start_time, end_time, clients)
            return report
        else:
            return empty_report()
    else:
        return empty_report()
