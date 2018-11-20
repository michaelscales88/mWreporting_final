#
from modules.utilities.helpers import get_model_by_tablename

from sqlalchemy import Column, Integer, ForeignKey, Table, String
from sqlalchemy.orm import relationship

from modules.extensions import BaseModel

from .client_model import ClientModel

user_model = get_model_by_tablename("user")

client_user_association = Table(
    'client_manager_association', BaseModel.metadata,
    Column('client_manager_id', Integer, ForeignKey('client_manager.id')),
    Column('client_model_id', Integer, ForeignKey('client_model.id'))
)

user_manager_association = Table(
    'user_manager_association', BaseModel.metadata,
    Column('user_id', Integer, ForeignKey('user.id')),
    Column('manager_id', Integer, ForeignKey('client_manager.id'))
)


class ClientManager(BaseModel):
    __tablename__ = 'client_manager'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))

    managers = relationship(
        user_model,
        secondary=user_manager_association,
        cascade='all'
    )

    clients = relationship(
        ClientModel,
        secondary=client_user_association,
        cascade='all'
    )

    def __str__(self):
        return str(self.name)
