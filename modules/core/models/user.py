# security/models.py
from flask_security import UserMixin
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship

from modules.base.base_model import BaseModel
from .associations import users_roles_association
from .roles import RolesModel


class UserModel(BaseModel, UserMixin):
    """ User Model for storing user related details """
    __tablename__ = "user"
    __repr_attrs__ = ['username']

    id = Column(Integer, primary_key=True)

    # User authentication information
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(255), nullable=False, server_default='')

    # User email information
    email = Column(String(255), unique=True)
    confirmed_at = Column(DateTime(timezone=True))

    # User information
    active = Column('is_active', Boolean, nullable=False, default=True)
    first_name = Column(String(100), nullable=False, server_default='')
    last_name = Column(String(100), nullable=False, server_default='')

    roles = relationship(
        RolesModel,
        secondary=users_roles_association,
        backref="users",
        lazy="dynamic"
    )

    @classmethod
    def get(cls, uid):
        return cls.query.filter(cls.id == uid).first()

    def __str__(self):
        return "{last}, {first}".format(
            last=self.last_name, first=self.first_name
        )
