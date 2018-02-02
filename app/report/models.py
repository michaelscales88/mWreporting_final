# report/models.py
from sqlalchemy.ext.hybrid import hybrid_property

from app.services import json_type
from app import db


class SlaReportModel(db.Model):
    __tablename__ = 'sla_report'
    __repr_attrs__ = ['id', 'start_time', 'end_time', 'data']

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    data = db.Column(json_type)

    @hybrid_property
    def headers(self):
        return [
            'I/C Presented',
            'I/C Live Answered',
            'I/C Abandoned',
            'Voice Mails',
            'Incoming Live Answered (%)',
            'Incoming Received (%)',
            'Incoming Abandoned (%)',
            'Average Incoming Duration',
            'Average Wait Answered',
            'Average Wait Lost',
            'Lost Wait Duration',
            'Calls Ans Within 15',
            'Calls Ans Within 30',
            'Calls Ans Within 45',
            'Calls Ans Within 60',
            'Calls Ans Within 999',
            'Call Ans + 999',
            'Longest Waiting Answered',
            'PCA'
        ]


_mmap = {
    "sla_report": SlaReportModel
}
