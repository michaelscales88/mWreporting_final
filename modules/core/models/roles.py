# user/models/roles.py
from flask_security import RoleMixin
from sqlalchemy import Column, Integer, String

from modules.base.base_model import BaseModel


class RolesModel(BaseModel, RoleMixin):
    __tablename__ = 'roles'
    __repr_attrs__ = ['name']
    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True, nullable=False)

    def __str__(self):
        return self.name
