# data/models.py
from datetime import datetime, timedelta
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import and_, func


from backend.services.extensions import db


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


class TablesLoaded(db.Model):

    __tablename__ = 'tables_loaded'
    __repr_attrs__ = ['date_loaded', 'dt_downloaded']

    id = db.Column(db.Integer, primary_key=True)
    date_loaded = db.Column(db.Date, nullable=False)
    table = db.Column(db.String, nullable=False)
    dt_downloaded = db.Column(db.DateTime, default=datetime.now())

    @classmethod
    def check_date_set(cls, date, table_name):
        return cls.query.filter(
            and_(
                cls.date_loaded == date,
                cls.table == table_name
            )
        ).first()

    @classmethod
    def check_date_interval(cls, start_time, end_time, table_name):
        """
        Return True if the data is loaded for the interval, or False
        if any day is not loaded.
        """
        while start_time < end_time:
            if cls.query.filter(
                and_(
                    cls.date_loaded == func.DATE(start_time),
                    cls.table == table_name
                )
            ).first() is None:
                return False
            start_time += timedelta(days=1)
        return True


_mmap = {
    'c_call': CallTableModel,
    'c_event': EventTableModel,
    'tables_loaded': TablesLoaded
}
