from celery.schedules import crontab
from .getters import *
from .loaders import *
from .report_tasks import *


def register_report_tasks(server_instance):
    """ Report Data """
    server_instance.config['CELERYBEAT_SCHEDULE']['load_report_data'] = {
        'task': 'report.utilities.data_loader',
        'schedule': crontab(
            **{server_instance.config['BEAT_PERIOD']: server_instance.config['BEAT_RATE']}
        )
    }

    """ SLA Report """
    server_instance.config['CELERYBEAT_SCHEDULE']['load_report'] = {
        'task': 'report.utilities.report_loader',
        'schedule': crontab(
            **{server_instance.config['BEAT_PERIOD']: server_instance.config['BEAT_RATE']}
        )
    }

    """ Summary SLA Report """
    # server_instance.config['CELERYBEAT_SCHEDULE']['load_summary_report'] = {
    #     'task': 'report.utilities.summary_report_loader',
    #     'schedule': crontab(
    #         **{server_instance.config['BEAT_PERIOD']: server_instance.config['BEAT_RATE']}
    #     )
    # }