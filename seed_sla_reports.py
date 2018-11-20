import datetime
from modules import app
from modules.utilities import get_model_by_tablename


def add_reports():

    with app.app_context():
        start_dt = datetime.datetime.strptime(str(input("What date to start?")), "%m/%d/%Y")
        days_to_load = int(input("How many days to load from the start time?"))
        counter = 0

        sla_report_model = get_model_by_tablename("sla_report")

        while counter < days_to_load:
            date = start_dt + datetime.timedelta(days=counter)
            sla_report_model.create(
                start_time=date.replace(hour=7, minute=0, second=0, microsecond=0),
                end_time=date.replace(hour=19, minute=0, second=0, microsecond=0)
            )
            counter += 1

        sla_report_model.session.commit()
        sla_report_model.session.remove()


if __name__ == '__main__':
    add_reports()
