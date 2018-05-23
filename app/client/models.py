# client/models.py
from app.extensions import db


class ClientModel(db.Model):

    __tablename__ = 'client'
    __repr_attrs__ = ['id', 'client_name', 'ext', 'active']

    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.Text, nullable=False)
    ext = db.Column(db.Integer, nullable=False)
    active = db.Column(db.Boolean, default=True)

    @classmethod
    def get(cls, ext):
        return cls.query.filter(cls.ext == int(ext)).first()


_mmap = {
    "client": ClientModel
}
