import datetime
from modules import app
from modules.core import get_model_by_tablename


def add_dates():

    with app.app_context():
        start_dt = datetime.datetime.strptime(str(input("What date to start?")), "%m/%d/%Y")
        days_to_load = int(input("How many days to load from the start time?"))
        counter = 0

        load_table = get_model_by_tablename("loaded_tables")

        while counter < days_to_load:
            load_table.create(loaded_date=(start_dt + datetime.timedelta(days=counter)))
            counter += 1

        load_table.session.commit()
        load_table.session.remove()


if __name__ == '__main__':
    add_dates()
