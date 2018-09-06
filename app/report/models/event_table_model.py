# data/models.py
import datetime
from sqlalchemy.ext.hybrid import hybrid_property

from app.extensions import db
from .call_table_model import CallTableModel


class EventTableModel(db.Model):
    __tablename__ = 'c_event'
    __repr_attrs__ = ['event_id', 'event_type', 'calling_party', 'receiving_party',
                      'is_conference', 'start_time', 'end_time', 'call_id']

    event_id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.Integer, nullable=False)
    calling_party = db.Column(db.String)
    receiving_party = db.Column(db.String)
    hunt_group = db.Column(db.String)
    is_conference = db.Column(db.String)
    start_time = db.Column(db.DateTime(timezone=True), nullable=False)
    end_time = db.Column(db.DateTime(timezone=True), nullable=False)
    tag = db.Column(db.String)
    recording_rule = db.Column(db.Integer)
    call_id = db.Column(db.Integer, db.ForeignKey(CallTableModel.call_id))

    @hybrid_property
    def length(self):
        delta = self.end_time - self.start_time
        return delta - datetime.timedelta(microseconds=delta.microseconds)

    @classmethod
    def set_empty(cls, model):
        model.data = {}
        return model
