# tasks/model.py
from sqlalchemy import Column, Integer, DateTime, String, Boolean, Text, Time
from sqlalchemy.ext.hybrid import hybrid_property

from modules.extensions import BaseModel
from modules.utilities.helpers import utc_now


class ScheduleDispatchItemModel(BaseModel):
    __tablename__ = 'scheduled_items'
    __repr_attrs__ = ['name']

    """ View information """
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False, unique=True)
    model_type = Column(String(20), nullable=False)     # Activity by __tablename__
    description = Column(Text)

    """ Housekeeping """
    active = Column(Boolean, default=True)
    date_created = Column(DateTime(timezone=True), default=utc_now())
    last_active = Column(DateTime(timezone=True))

    """ Interval Information """
    when_to_run = Column(String(10), nullable=False)    # schedule_type
    time_to_run = Column(Time, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    def __str__(self):
        return self.name

    @hybrid_property
    def task_type(self):
        return self.model_type

    @hybrid_property
    def scheduled_time(self):
        if self.when_to_run == "Hourly":
            return ""
        if self.when_to_run == "Daily":
            return ""
        if self.when_to_run == "Monthly":
            return ""
        return "Unrecognized Configuration"
