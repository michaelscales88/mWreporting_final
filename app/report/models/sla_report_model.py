# report/models.py
import datetime
from sqlalchemy.sql import and_

from app.encoders import json_type
from app.extensions import db


class SlaReportModel(db.Model):
    __tablename__ = 'sla_report'
    __repr_attrs__ = ['id', 'start_time', 'end_time', 'completed_on']

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    data = db.Column(json_type)

    date_requested = db.Column(db.DateTime, default=datetime.datetime.now())
    last_updated = db.Column(db.DateTime)
    completed_on = db.Column(db.DateTime)

    @classmethod
    def headers(cls):
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
