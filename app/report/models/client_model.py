# client/models.py
from app.extensions import db


class ClientModel(db.Model):

    __tablename__ = 'client_model'
    __repr_attrs__ = ['name', 'active']

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    ext = db.Column(db.Integer, nullable=False)
    active = db.Column(db.Boolean, default=True)

    notes = db.Column(db.Text)

    def __str__(self):
        return self.name
