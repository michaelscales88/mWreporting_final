from app import db
from app.util import json_type


class SLAReport(db.Model):

    __tablename__ = 'sla_report'
    __repr_attrs__ = ['id', 'start_time', 'end_time', 'report', 'notes']

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    report = db.Column(json_type)
    notes = db.Column(db.Text)
