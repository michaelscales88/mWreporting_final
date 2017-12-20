from sqlalchemy import Column, Text, DateTime, Integer

from app import db
from app.util import json_type


class SLAReport(db.Model):

    __tablename__ = 'sla_report'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    report = Column(json_type)
    notes = Column(Text)
