# tasks/model.py
import datetime
from modules.extensions import db


class ScheduleDispatchItemModel(db.Model):
    __tablename__ = 'scheduled_items'
    __repr_attrs__ = ['name']

    """ View information """
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.Text)

    """ Housekeeping """
    active = db.Column(db.Boolean(), nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow())
    last_active = db.Column(db.DateTime(timezone=True))

    """ Interval Information """
    when_to_run = db.Column(db.String(1), default='D')
    start_time = db.Column(db.Time(), nullable=False)
    end_time = db.Column(db.Time(), nullable=False)

    """ Activity by __tablename__"""
    what_to_run = db.Column(db.String(10))

    def __str__(self):
        return self.name
