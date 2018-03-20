# report/tasks.py
from backend.report.services import get_sla_report, empty_report


def report_task(report_name, start_time=None, end_time=None, clients=None):
    print("hit report_task", report_name, start_time, end_time, clients)
    if report_name == 'sla_report':
        if start_time and end_time:
            report = get_sla_report(start_time, end_time, clients)
            return report
        else:
            return empty_report()
    else:
        return empty_report()
