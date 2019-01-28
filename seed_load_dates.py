import datetime

from modules import app
from modules.report.utilities import signals as s


def add_dates():
    with app.app_context():
        start_dt = datetime.datetime.strptime(str(input("What date to start?")), "%m/%d/%Y")
        days_to_load = int(input("How many days to load from the start time?"))
        counter = 0

        while counter < days_to_load:
            loaded_date = start_dt + datetime.timedelta(days=counter)
            s.load_calls(loaded_date, with_events=True)
            counter += 1


if __name__ == '__main__':
    add_dates()
