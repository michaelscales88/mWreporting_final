# client/models.py
from sqlalchemy import Column, Integer, String, Boolean, Text

from modules.base.base_model import BaseModel


class ClientModel(BaseModel):

    __tablename__ = 'client_model'
    __repr_attrs__ = ['name', 'active']

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    ext = Column(Integer, nullable=False)
    active = Column(Boolean, default=True)

    notes = Column(Text)

    def __str__(self):
        return self.name
