# data/models.py
from sqlalchemy.ext.hybrid import hybrid_property

from app import db


class CallTableModel(db.Model):

    __tablename__ = 'c_call'
    __repr_attrs__ = ['call_id', 'calling_party_number', 'dialed_party_number',
                      'start_time', 'end_time', 'caller_id']

    call_id = db.Column(db.Integer, primary_key=True)
    call_direction = db.Column(db.Integer)
    calling_party_number = db.Column(db.Text)
    dialed_party_number = db.Column(db.Text)
    account_code = db.Column(db.Text)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    system_id = db.Column(db.Integer)
    caller_id = db.Column(db.Text)
    inbound_route = db.Column(db.Text)
    events = db.relationship("EventTableModel", lazy="dynamic")

    @hybrid_property
    def length(self):
        return self.end_time - self.start_time


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


_mmap = {
    'c_call': CallTableModel,
    'c_event': EventTableModel
}
