# user/models/associations.py
from sqlalchemy import Column, Table, Integer, ForeignKey
from modules.extensions import BaseModel


users_roles_association = Table(
    'users_roles_association', BaseModel.metadata,
    Column('user_id', Integer, ForeignKey('user.id')),
    Column('role_id', Integer, ForeignKey('roles.id'))
)
