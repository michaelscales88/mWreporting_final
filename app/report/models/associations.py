#
import datetime
from app.extensions import db
from sqlalchemy.sql import and_, func


from app.utilities import get_model_by_tablename
from .client_model import ClientModel


user_model = get_model_by_tablename("user")


class TablesLoadedModel(db.Model):

    __tablename__ = 'loaded_tables'
    __repr_attrs__ = ['loaded_date', 'table', 'date_downloaded']

    id = db.Column(db.Integer, primary_key=True)
    table = db.Column(db.String, nullable=False)
    loaded_date = db.Column(db.Date, nullable=False)

    date_requested = db.Column(db.DateTime, default=datetime.datetime.now())
    date_downloaded = db.Column(db.DateTime)

    is_loaded = db.Column(db.Boolean, default=False)

    @classmethod
    def find_table_by_date(cls, loaded_date, table_name):
        return cls.query.filter(
            and_(
                cls.loaded_date == func.DATE(loaded_date),
                cls.table == table_name
            )
        ).first()

    @classmethod
    def check_date_set(cls, date, table_name):
        return cls.find_table_by_date(date, table_name) is not None

    @classmethod
    def check_date_interval(cls, start_time, end_time, table_name):
        """
        Return True if the data is loaded for the interval, or Falsea
        if any day is not loaded.
        """
        while start_time < end_time:
            if cls.find_table_by_date(start_time, table_name) is None:
                return False
            start_time += datetime.timedelta(days=1)
        return True


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
