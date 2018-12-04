# report/models.py
import datetime

from sqlalchemy import Column, Integer, DateTime, Boolean
from sqlalchemy.sql import and_

from modules.core.encoders import JSONEncodedDict
from modules.extensions import BaseModel
from modules.utilities.helpers import utc_now


class SlaReportModel(BaseModel):
    __tablename__ = 'sla_report'
    __repr_attrs__ = ['id', 'start_time', 'end_time', 'completed_on']

    id = Column(Integer, primary_key=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    data = Column(JSONEncodedDict)
    is_schedulable = Column(Boolean, default=True)

    date_requested = Column(DateTime, default=utc_now())
    last_updated = Column(DateTime)
    completed_on = Column(DateTime)

    @staticmethod
    def opt_name():
        return "SLA Report"

    @staticmethod
    def view_headers():
        return [
            'I/C Presented',
            'I/C Live Answered',
            'I/C Lost',
            'Voice Mails',
            'Incoming Live Answered (%)',
            'Incoming Received (%)',
            'Incoming Abandoned (%)',
            'Average Incoming Duration',
            'Average Wait Answered',
            'Average Wait Lost',
            'Calls Ans Within 15',
            'Calls Ans Within 30',
            'Calls Ans Within 45',
            'Calls Ans Within 60',
            'Calls Ans Within 999',
            'Call Ans + 999',
            'Longest Waiting Answered',
            'PCA'
        ]

    @classmethod
    def default_row(cls):
        return zip(cls.data_headers(), cls.default_row_vals())

    @staticmethod
    def data_headers():
        return [
            'I/C Presented',
            'I/C Live Answered',
            'I/C Lost',
            'Voice Mails',
            'Answered Incoming Duration',
            'Answered Wait Duration',
            'Lost Wait Duration',
            'Calls Ans Within 15',
            'Calls Ans Within 30',
            'Calls Ans Within 45',
            'Calls Ans Within 60',
            'Calls Ans Within 999',
            'Call Ans + 999',
            'Longest Waiting Answered'
        ]

    @staticmethod
    def default_row_vals():
        return [
            0,  # 'I/C Presented'
            0,  # 'I/C Live Answered'
            0,  # 'I/C Abandoned'
            0,  # 'Voice Mails'
            datetime.timedelta(0),  # Answered Incoming Duration
            datetime.timedelta(0),  # Answered Wait Duration
            datetime.timedelta(0),  # Lost Wait Duration
            0,  # 'Calls Ans Within 15'
            0,  # 'Calls Ans Within 30'
            0,  # 'Calls Ans Within 45'
            0,  # 'Calls Ans Within 60'
            0,  # 'Calls Ans Within 999'
            0,  # 'Call Ans + 999'
            datetime.timedelta(0)  # 'Longest Waiting Answered'
        ]

    @classmethod
    def get(cls, start_time, end_time):
        return cls.query.filter(
            and_(
                cls.start_time == start_time,
                cls.end_time == end_time
            )
        ).first()

    @classmethod
    def exists(cls, start_time, end_time):
        return cls.get(start_time, end_time) is not None

    @classmethod
    def set_empty(cls, model):
        model.data = {}
        return model

    @classmethod
    def interval_is_loaded(cls, start_time, end_time, interval):
        """
        Return True if the data is loaded for the interval, or False
        if any day is not loaded.
        """
        if isinstance(interval, int):
            interval = datetime.timedelta(seconds=interval)

        if not isinstance(interval, datetime.timedelta):
            return None

        while start_time < end_time:
            end_dt = start_time + interval
            # Does not exist
            if not cls.get(start_time, end_dt):
                return False
            start_time = end_dt
        return True
