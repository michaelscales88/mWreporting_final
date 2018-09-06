#
import datetime

from sqlalchemy.ext.hybrid import hybrid_property

from app.extensions import db


class TablesLoadedModel(db.Model):

    __tablename__ = 'loaded_tables'
    __repr_attrs__ = ['loaded_date', 'last_updated', 'complete']

    id = db.Column(db.Integer, primary_key=True)
    loaded_date = db.Column(db.Date, nullable=False, unique=True)

    date_requested = db.Column(db.DateTime(timezone=True), default=datetime.datetime.now())
    last_updated = db.Column(db.DateTime(timezone=True))

    calls_loaded = db.Column(db.Boolean, default=False)
    events_loaded = db.Column(db.Boolean, default=False)

    @hybrid_property
    def complete(self):
        return self.is_loaded(self.loaded_date)

    @classmethod
    def find(cls, date):
        return cls.query.filter(
            cls.loaded_date == date
        ).first()

    @classmethod
    def is_loaded(cls, date):
        record = cls.find(
            date.date() if isinstance(date, datetime.datetime) else date
        )
        return record and record.calls_loaded and record.events_loaded

    @classmethod
    def interval_is_loaded(cls, start_time, end_time):
        """
        Return True if the data is loaded for the interval, or False
        if any day is not loaded.
        """
        while start_time < end_time:
            if not cls.is_loaded(start_time):
                return False
            start_time += datetime.timedelta(days=1)
        return True

    @classmethod
    def not_loaded_when2when(cls, start_time, end_time):
        """
        Return True if the data is loaded for the interval, or False
        if any day is not loaded.
        """
        while start_time < end_time:
            if cls.find(start_time) is None:
                yield start_time
            start_time += datetime.timedelta(days=1)

    @classmethod
    def add_interval(cls, start_time, end_time):
        """
        Return True if the data is loaded for the interval, or False
        if any day is not loaded.
        """
        start_date = (
            start_time.date()
            if isinstance(start_time, datetime.datetime)
            else start_time
        )
        end_date = (
            end_time.date()
            if isinstance(end_time, datetime.datetime)
            else end_time
        )
        while start_date < end_date:
            if not cls.find(start_date):
                cls.create(loaded_date=start_date)
            start_time += datetime.timedelta(days=1)
