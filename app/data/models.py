from sqlalchemy.exc import DatabaseError
from sqlalchemy.ext.hybrid import hybrid_property


from app import app, db
from app.database import get_scoped_session
from app.util.base_models import GetOrQuery


ext_data_session = get_scoped_session(app, db, 'ext_data')
loc_data_session = get_scoped_session(app, db, None)


class CallTable(db.Model):

    __bind_key__ = 'ext_data'
    __tablename__ = 'c_call'
    __repr_attrs__ = ['call_id', 'calling_party_number', 'dialed_party_number', 'start_time', 'end_time', 'caller_id']
    query = ext_data_session.query_property()

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


class EventTable(db.Model):

    __bind_key__ = 'ext_data'
    __tablename__ = 'c_event'
    __repr_attrs__ = ['event_id', 'event_type', 'calling_party', 'receiving_party',
                      'is_conference', 'start_time', 'end_time', 'call_id']
    query = ext_data_session.query_property()

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


class LocalSessionMixin(object):

    __bind_key__ = None
    session = loc_data_session
    query = session.query_property(query_cls=GetOrQuery)


class LocalCallTable(LocalSessionMixin, db.Model):

    __tablename__ = 'loc_call'
    __repr_attrs__ = ['call_id', 'calling_party_number', 'dialed_party_number', 'start_time', 'end_time', 'caller_id']

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

    def __init__(self, call_id=None, call_direction=None, calling_party_number='',
                 dialed_party_number='', account_code='', start_time=None,
                 end_time=None, system_id=None, caller_id='', inbound_route='',
                 **kwargs):
        super().__init__()
        self.call_id = call_id
        self.call_direction = call_direction
        self.calling_party_number = calling_party_number
        self.dialed_party_number = dialed_party_number
        self.account_code = account_code
        self.start_time = start_time
        self.end_time = end_time
        self.system_id = system_id
        self.caller_id = caller_id
        self.inbound_route = inbound_route

    @hybrid_property
    def length(self):
        return self.end_time - self.start_time


class LocalEventTable(LocalSessionMixin, db.Model):

    __tablename__ = 'loc_event'
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
    call_id = db.Column(db.Integer, db.ForeignKey(CallTable.call_id))

    def __init__(self, event_id=None, event_type=None, calling_party='',
                 receiving_party='', hunt_group='', is_conference=None,
                 start_time=None, end_time=None, tag='', recording_rule='',
                 call_id=None, **kwargs):
        super().__init__()
        self.event_id = event_id
        self.event_type = event_type
        self.calling_party = calling_party
        self.receiving_party = receiving_party
        self.hunt_group = hunt_group
        self.is_conference = is_conference
        self.start_time = start_time
        self.end_time = end_time
        self.tag = tag
        self.recording_rule = recording_rule
        self.call_id = call_id

    @hybrid_property
    def length(self):
        return self.end_time - self.start_time
