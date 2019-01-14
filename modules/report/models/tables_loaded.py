#
import datetime

from sqlalchemy import Column, Integer, DateTime, Date, Boolean, func
from sqlalchemy.ext.hybrid import hybrid_property

from modules.extensions import BaseModel
from modules.utilities.helpers import utc_now


class TablesLoadedModel(BaseModel):

    __tablename__ = 'loaded_tables'
    __repr_attrs__ = ['loaded_date', 'last_updated', 'complete']

    id = Column(Integer, primary_key=True)
    loaded_date = Column(Date, nullable=False, unique=True)

    date_requested = Column(DateTime(timezone=True), default=utc_now())
    last_updated = Column(DateTime(timezone=True))
    is_schedulable = Column(Boolean, default=True)

    calls_loaded = Column(Boolean, default=False)
    events_loaded = Column(Boolean, default=False)

    @staticmethod
    def opt_name():
        return "Raw Data Loader"

    @hybrid_property
    def complete(self):
        if isinstance(self.loaded_date, datetime.date):
            return self.is_loaded(self.loaded_date)
        else:
            return False

    @classmethod
    def find(cls, date):
        return cls.query.filter(cls.loaded_date == func.date(date)).first()

    @classmethod
    def worker_find(cls, session, date):
        return session.query(cls).filter(cls.loaded_date == func.date(date)).first()

    @classmethod
    def is_loaded(cls, date):
        record = cls.find(date)
        if record:
            return record and record.calls_loaded and record.events_loaded
        else:
            return False

    @classmethod
    def worker_is_loaded(cls, session, date):
        record = cls.worker_find(session, date)
        if record:
            return record and record.calls_loaded and record.events_loaded
        else:
            return False

    @classmethod
    def interval_is_loaded(cls, start_time, end_time):
        """
        Return True if the data is loaded for the interval, or False
        if any day is not loaded.
        """
        while start_time < end_time:
            if not cls.is_loaded(start_time):
                print("is not loaded", start_time)
                return False
            start_time += datetime.timedelta(days=1)
        return True

    @classmethod
    def worker_interval_is_loaded(cls, session, start_time, end_time):
        """
        Return True if the data is loaded for the interval, or False
        if any day is not loaded.
        """
        while start_time < end_time:
            if not cls.worker_is_loaded(session, start_time):
                print("is not loaded", start_time)
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
