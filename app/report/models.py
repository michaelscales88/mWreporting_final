# report/models.py
from app.util import json_type
from app import db


class SlaData(db.Model):

    __tablename__ = 'sla_report'
    __repr_attrs__ = ['id', 'start_time', 'end_time', 'data']

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    data = db.Column(db.JSON)


_mmap = {
    "sla_report": SlaData
}
