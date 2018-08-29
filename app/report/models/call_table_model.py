# data/models.py
import datetime
from sqlalchemy.ext.hybrid import hybrid_property

from app.extensions import db


class CallTableModel(db.Model):
    __tablename__ = 'c_call'
    __repr_attrs__ = ['call_id', 'calling_party_number', 'dialed_party_number',
                      'start_time', 'end_time', 'caller_id']

    call_id = db.Column(db.Integer, primary_key=True)
    call_direction = db.Column(db.Integer)
    calling_party_number = db.Column(db.String)
    dialed_party_number = db.Column(db.String)
    account_code = db.Column(db.String)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    system_id = db.Column(db.Integer)
    caller_id = db.Column(db.String)
    inbound_route = db.Column(db.String)
    events = db.relationship("EventTableModel", lazy="dynamic")

    @hybrid_property
    def length(self):
        delta = self.end_time - self.start_time
        return delta - datetime.timedelta(microseconds=delta.microseconds)

    @classmethod
    def set_empty(cls, model):
        model.data = {}
        return model
