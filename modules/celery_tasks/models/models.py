# tasks/model.py
import datetime
from sqlalchemy import Column, Integer, DateTime, String, Boolean, Text, Time

from modules.extensions import BaseModel


class ScheduleDispatchItemModel(BaseModel):
    __tablename__ = 'scheduled_items'
    __repr_attrs__ = ['name']

    """ View information """
    id = Column(Integer(), primary_key=True)
    name = Column(String(80), unique=True, nullable=False)
    description = Column(Text)

    """ Housekeeping """
    active = Column(Boolean(), nullable=False)
    date_created = Column(DateTime(timezone=True), default=datetime.datetime.utcnow())
    last_active = Column(DateTime(timezone=True))

    """ Interval Information """
    when_to_run = Column(String(1), default='D')
    start_time = Column(Time(), nullable=False)
    end_time = Column(Time(), nullable=False)

    """ Activity by __tablename__"""
    what_to_run = Column(String(10))

    def __str__(self):
        return self.name
