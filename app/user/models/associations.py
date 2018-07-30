# user/models/associations.py
from app.extensions import db

# client_user_association = db.Table(
#     'client_user_association', db.metadata,
#     db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
#     db.Column('client_id', db.Integer, db.ForeignKey('client.id'))
# )


users_roles_association = db.Table(
    'users_roles_association', db.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'))
)
