# client/models.py
from app import db


class ClientModel(db.Model):

    __tablename__ = 'client_table'
    __repr_attrs__ = ['id', 'client_name', 'ext', 'active']

    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.Text, nullable=False)
    ext = db.Column(db.Integer, nullable=False)
    active = db.Column(db.Boolean(create_constraint=False), default=True)


_mmap = {
    "client_table": ClientModel
}
