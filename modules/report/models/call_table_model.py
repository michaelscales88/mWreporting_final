# data/models.py
import datetime

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.hybrid import hybrid_property

from modules.extensions import BaseModel
from .event_table_model import EventTableModel


class CallTableModel(BaseModel):
    __tablename__ = 'c_call'
    __repr_attrs__ = [
        'call_id', 'calling_party_number', 'dialed_party_number',
        'start_time', 'end_time', 'caller_id'
    ]

    call_id = Column(Integer, primary_key=True)
    call_direction = Column(Integer)
    calling_party_number = Column(String(100))
    dialed_party_number = Column(String(100))
    account_code = Column(String(100))
    start_time = Column(DateTime(timezone=True))
    end_time = Column(DateTime(timezone=True))
    system_id = Column(Integer)
    caller_id = Column(String(100))
    inbound_route = Column(String(100))

    @hybrid_property
    def length(self):
        delta = self.end_time - self.start_time
        return delta - datetime.timedelta(microseconds=delta.microseconds)

    @classmethod
    def set_empty(cls, model):
        model.data = {}
        return model

    @hybrid_property
    def events(self):
        return EventTableModel.query.filter_by(call_id=self.call_id).all()
