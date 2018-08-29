# user/models/roles.py
from flask_security import RoleMixin
from app.extensions import db


class RolesModel(db.Model, RoleMixin):
    __tablename__ = 'roles'
    __repr_attrs__ = ['name']
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    def __str__(self):
        return self.name
