#
from modules.core import get_model_by_tablename

from sqlalchemy import Column, Integer, ForeignKey, Table
from sqlalchemy.orm import relationship

from modules.extensions import BaseModel

from .client_model import ClientModel

user_model = get_model_by_tablename("user")

client_user_association = Table(
    'client_manager_association', BaseModel.metadata,
    Column('client_manager_id', Integer, ForeignKey('client_manager.id')),
    Column('client_model_id', Integer, ForeignKey('client_model.id'))
)


class ClientManager(BaseModel):
    __tablename__ = 'client_manager'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer(), ForeignKey('user.id'))
    manager = relationship(user_model, backref="clients")

    clients = relationship(
        ClientModel,
        secondary=client_user_association,
        cascade='all'
    )

    def __str__(self):
        return str(self.manager)
