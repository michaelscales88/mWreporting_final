from sqlalchemy import Column, Text, DateTime, Integer

from app.database import Base
from app.util import json_type


class SLAReport(Base):
    __searchable__ = ['date', 'notes',]

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    report = Column(json_type)
    notes = Column(Text)
