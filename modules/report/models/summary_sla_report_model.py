# report/models.py
import datetime

from sqlalchemy import Column, Integer, DateTime, Boolean
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import and_

from modules.base.base_model import BaseModel
from modules.core.encoders import JSONEncodedDict
from modules.utilities.helpers import utc_now
from .sla_report_model import SlaReportModel


class SummarySLAReportModel(BaseModel):
    __tablename__ = 'sla_summary_report'
    __repr_attrs__ = ['id', 'start_time', 'end_time', 'interval']

    id = Column(Integer, primary_key=True)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    frequency = Column(Integer, default=86400)
    data = Column(JSONEncodedDict(1024))
    is_schedulable = Column(Boolean, default=True)

    date_requested = Column(DateTime(timezone=True), default=utc_now())
    last_updated = Column(DateTime(timezone=True))
    completed_on = Column(DateTime(timezone=True))

    @staticmethod
    def opt_name():
        return "SLA Summary Report"

    @hybrid_property
    def interval(self):
        if isinstance(self.frequency, int):
            try:
                return datetime.timedelta(seconds=self.frequency)
            except TypeError:
                return datetime.timedelta(0)

    @classmethod
    def headers(cls):
        return SlaReportModel.view_headers()

    @classmethod
    def get(cls, start_time, end_time, frequency):
        return cls.query.filter(
            and_(
                cls.start_time == start_time,
                cls.end_time == end_time,
                cls.frequency == frequency
            )
        ).first()

    @classmethod
    def exists(cls, start_time, end_time, interval):
        return cls.get(start_time, end_time, interval) is not None
