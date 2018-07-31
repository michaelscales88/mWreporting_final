# data/models.py
from sqlalchemy.ext.hybrid import hybrid_property

from app.extensions import db
from .call_table_model import CallTableModel


class EventTableModel(db.Model):
    __tablename__ = 'c_event'
    __repr_attrs__ = ['event_id', 'event_type', 'calling_party', 'receiving_party',
                      'is_conference', 'start_time', 'end_time', 'call_id']

    event_id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.Integer, nullable=False)
    calling_party = db.Column(db.Text)
    receiving_party = db.Column(db.Text)
    hunt_group = db.Column(db.Text)
    is_conference = db.Column(db.Text)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    tag = db.Column(db.Text)
    recording_rule = db.Column(db.Integer)
    call_id = db.Column(db.Integer, db.ForeignKey(CallTableModel.call_id))
    call = db.relationship("CallTableModel")

    @hybrid_property
    def length(self):
        return self.end_time - self.start_time

    @classmethod
    def set_empty(cls, model):
        model.data = {}
        return model
