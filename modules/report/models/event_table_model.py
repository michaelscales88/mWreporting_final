# data/models.py
import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.hybrid import hybrid_property

from modules.extensions import BaseModel
from .call_table_model import CallTableModel


class EventTableModel(BaseModel):
    __tablename__ = 'c_event'
    __repr_attrs__ = ['event_id', 'event_type', 'calling_party', 'receiving_party',
                      'is_conference', 'start_time', 'end_time', 'call_id']

    event_id = Column(Integer, primary_key=True)
    event_type = Column(Integer, nullable=False)
    calling_party = Column(String(50))
    receiving_party = Column(String(50))
    hunt_group = Column(String(50))
    is_conference = Column(String(10))
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    tag = Column(String(10))
    recording_rule = Column(Integer)
    call_id = Column(Integer, ForeignKey(CallTableModel.call_id))

    @hybrid_property
    def length(self):
        delta = self.end_time - self.start_time
        return delta - datetime.timedelta(microseconds=delta.microseconds)

    @classmethod
    def set_empty(cls, model):
        model.data = {}
        return model
