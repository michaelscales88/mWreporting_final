# security/models.py
from flask_security import UserMixin

from app.extensions import db
from .associations import users_roles_association
from .roles import RolesModel


class UserModel(db.Model, UserMixin):
    """ User Model for storing user related details """
    __tablename__ = "user"
    __repr_attrs__ = ['username']
    id = db.Column(db.Integer, primary_key=True)

    # User authentication information
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, server_default='')

    # User email information
    email = db.Column(db.String(255), nullable=False, unique=True)
    confirmed_at = db.Column(db.DateTime())

    # User information
    active = db.Column('is_active', db.Boolean(), nullable=False, default=1)
    first_name = db.Column(db.String(100), nullable=False, server_default='')
    last_name = db.Column(db.String(100), nullable=False, server_default='')

    # clients = db.relationship(
    #     "ClientModel",
    #     secondary=client_user_association,
    #     backref="users",
    #     cascade='all'
    # )

    roles = db.relationship(
        RolesModel,
        secondary=users_roles_association,
        backref="users",
        lazy="dynamic"
    )

    @classmethod
    def get(cls, uid):
        return cls.query.filter(cls.id == uid).first()
