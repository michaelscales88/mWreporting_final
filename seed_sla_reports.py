import datetime

from modules import app
from modules.report.tasks import report_task


def add_reports():
    with app.app_context():
        start_dt = datetime.datetime.strptime(str(input("What date to start?")), "%m/%d/%Y")
        days_to_load = int(input("How many days to load from the start time?"))
        counter = 0

        while counter < days_to_load:
            date = start_dt + datetime.timedelta(days=counter)
            start_time = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_time = date.replace(hour=23, minute=59, second=0, microsecond=0)
            report_task.delay(start_time=start_time, end_time=end_time)
            counter += 1


if __name__ == '__main__':
    add_reports()
