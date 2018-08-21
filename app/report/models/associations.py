#
import datetime
from app.extensions import db
from sqlalchemy.sql import func
from sqlalchemy.ext.hybrid import hybrid_property


from app.core import get_model_by_tablename
from .client_model import ClientModel


user_model = get_model_by_tablename("user")


class TablesLoadedModel(db.Model):

    __tablename__ = 'loaded_tables'
    __repr_attrs__ = ['loaded_date', 'last_updated', 'complete']

    id = db.Column(db.Integer, primary_key=True)
    loaded_date = db.Column(db.Date, nullable=False)

    date_requested = db.Column(db.DateTime, default=datetime.datetime.now())
    last_updated = db.Column(db.DateTime)

    calls_loaded = db.Column(db.Boolean, default=False)
    events_loaded = db.Column(db.Boolean, default=False)

    @hybrid_property
    def complete(self):
        return self.is_loaded(self.loaded_date)

    @classmethod
    def find(cls, date):
        return cls.query.filter(
            cls.loaded_date == func.DATE(date)
        ).first()

    @classmethod
    def is_loaded(cls, date):
        record = cls.find(date)
        return record and record.calls_loaded and record.events_loaded

    @classmethod
    def interval_is_loaded(cls, start_time, end_time):
        """
        Return True if the data is loaded for the interval, or False
        if any day is not loaded.
        """
        while start_time < end_time:
            if not cls.is_loaded(start_time):
                return False
            start_time += datetime.timedelta(days=1)
        return True

    @classmethod
    def not_loaded_when2when(cls, start_time, end_time):
        """
        Return True if the data is loaded for the interval, or False
        if any day is not loaded.
        """
        while start_time < end_time:
            if cls.find(start_time) is None:
                yield start_time
            start_time += datetime.timedelta(days=1)


client_user_association = db.Table(
    'client_manager_association', db.metadata,
    db.Column('client_manager_id', db.Integer, db.ForeignKey('client_manager.id')),
    db.Column('client_model_id', db.Integer, db.ForeignKey('client_model.id'))
)


class ClientManager(db.Model):
    __tablename__ = 'client_manager'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    manager = db.relationship(user_model, backref="clients")

    clients = db.relationship(
        ClientModel,
        secondary=client_user_association,
        cascade='all'
    )

    def __str__(self):
        return str(self.manager)
