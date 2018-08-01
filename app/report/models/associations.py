#
import datetime
from app.extensions import db
from sqlalchemy.sql import and_, func


from app.utilities import get_model_by_tablename

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
    def check_date_set(cls, date, table_name):
        print("checking date set")
        return cls.query.filter(
            and_(
                cls.date_loaded == date,
                cls.table == table_name,
                cls.is_loaded is True
            )
        ).first() is not None

    @classmethod
    def check_date_interval(cls, start_time, end_time, table_name):
        """
        Return True if the data is loaded for the interval, or Falsea
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
            start_time += datetime.timedelta(days=1)
        return True


class ClientManagerAssociation(db.Model):
    __tablename__ = 'client_manager_association'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client_table.id'), primary_key=True)
    manager = db.relationship(user_model, backref="clients")

    def __str__(self):
        return str(self.manager)
