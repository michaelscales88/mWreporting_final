# tasks/model.py
from app.extensions import db


class ScheduleItemModel(db.Model):
    __tablename__ = 'scheduled_items'
    __repr_attrs__ = ['name']
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    active = db.Column(db.Boolean(), nullable=False)
    start_time = db.Column(db.DateTime(), nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)

    def __str__(self):
        # Necessary for showing the role name
        return self.name
