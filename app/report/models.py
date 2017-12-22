from app import db
from app.util import json_type


class SLAReport(db.Model):

    __bind_key__ = None
    __tablename__ = 'sla_report'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    report = db.Column(json_type)
    notes = db.Column(db.Text)
