from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_mixins import AllFeaturesMixin


from app import db


class CallTable(AllFeaturesMixin, db.Model):

    __bind_key__ = ''
    __tablename__ = 'c_call'

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


class EventTable(AllFeaturesMixin, db.Model):

    __bind_key__ = ''
    __tablename__ = 'c_event'

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
    call_id = db.Column(db.Integer, db.ForeignKey(CallTable.call_id))

    @hybrid_property
    def length(self):
        return self.end_time - self.start_time
