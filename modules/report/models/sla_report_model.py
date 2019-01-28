# report/models.py
import datetime

from sqlalchemy import Column, Integer, DateTime, Boolean
from sqlalchemy.sql import and_

from modules.core.encoders import JSONEncodedDict
from modules.base.base_model import BaseModel
from modules.utilities.helpers import utc_now


class SlaReportModel(BaseModel):
    __tablename__ = 'sla_report'
    __repr_attrs__ = ['start_time', 'end_time']

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
    def find(cls, start_time, end_time):
        return cls.query.filter(
            and_(
                cls.start_time == start_time,
                cls.end_time == end_time
            )
        ).first()


class WorkerSlaReportModel(SlaReportModel):

    @classmethod
    def find(cls, session, start_time, end_time):
        return session.query(cls).filter(
            and_(
                cls.start_time == start_time,
                cls.end_time == end_time
            )
        ).first()
