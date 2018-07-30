# user/models/associations.py
from app.extensions import db


users_roles_association = db.Table(
    'users_roles_association', db.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'))
)
