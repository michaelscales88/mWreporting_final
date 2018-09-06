# report/models.py
import datetime
from sqlalchemy.sql import and_
from sqlalchemy.ext.hybrid import hybrid_property
from app.encoders import json_type
from app.extensions import db
from .sla_report_model import SlaReportModel


class SummarySLAReportModel(db.Model):
    __tablename__ = 'sla_summary_report'
    __repr_attrs__ = ['id', 'start_time', 'end_time', 'interval']

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime(timezone=True), nullable=False)
    end_time = db.Column(db.DateTime(timezone=True), nullable=False)
    frequency = db.Column(db.Integer, default=86400)
    data = db.Column(json_type)

    date_requested = db.Column(db.DateTime(timezone=True), default=datetime.datetime.now())
    last_updated = db.Column(db.DateTime(timezone=True))
    completed_on = db.Column(db.DateTime(timezone=True))

    @hybrid_property
    def interval(self):
        if isinstance(self.frequency, int):
            try:
                return datetime.timedelta(seconds=self.frequency)
            except TypeError:
                return datetime.timedelta(0)

    @classmethod
    def headers(cls):
        return SlaReportModel.headers()

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
