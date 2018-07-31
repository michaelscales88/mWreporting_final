# from datetime import datetime
import datetime
from app.extensions import db
from sqlalchemy.sql import and_, func


class TablesLoaded(db.Model):

    __tablename__ = 'tables_loaded'
    __repr_attrs__ = ['date_loaded', 'dt_downloaded']

    id = db.Column(db.Integer, primary_key=True)
    date_loaded = db.Column(db.Date, nullable=False)
    table = db.Column(db.String, nullable=False)
    dt_downloaded = db.Column(db.DateTime, default=datetime.datetime.now())

    @classmethod
    def check_date_set(cls, date, table_name):
        print("checking date set")
        return cls.query.filter(
            and_(
                cls.date_loaded == date,
                cls.table == table_name
            )
        ).first()

    @classmethod
    def check_date_interval(cls, start_time, end_time, table_name):
        """
        Return True if the data is loaded for the interval, or False
        if any day is not loaded.
        """
        while start_time < end_time:
            if cls.query.filter(
                and_(
                    cls.date_loaded == func.DATE(start_time),
                    cls.table == table_name
                )
            ).first() is None:
                return False
            start_time += datetime.timedelta(days=1)
        return True
