from app import app, db

from app.database import get_scoped_session
from app.util.base_models import GetOrQuery


app_meta_session = get_scoped_session(app, db, 'app_meta')


class Client(db.Model):

    __bind_key__ = 'app_meta'
    __tablename__ = 'client_table'
    __repr_attrs__ = ['id', 'client_name', 'ext', 'active']
    query = app_meta_session.query_property(query_cls=GetOrQuery)

    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.Text, nullable=False)
    ext = db.Column(db.Integer, nullable=False)
    active = db.Column(db.Boolean(create_constraint=False), default=True)
