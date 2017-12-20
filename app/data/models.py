from sqlalchemy import Column, Text, DateTime, Integer, ForeignKey
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.declarative import declared_attr
from app.database import Base


class CallTable(Base):
    __searchable__ = []

    @declared_attr
    def __tablename__(cls):
        return 'c_call'

    """
    Parent table
    """
    call_id = Column(Integer, primary_key=True)
    call_direction = Column(Integer)
    calling_party_number = Column(Text)
    dialed_party_number = Column(Text)
    account_code = Column(Text)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    system_id = Column(Integer)
    caller_id = Column(Text)
    inbound_route = Column(Text)

    def __json__(self):
        return list(self.__mapper__.columns.keys())

    def __lt__(self, other):
        # Gives CallTable a sortable property
        return self.call_id < other.call_id


class EventTable(Base):
    __searchable__ = []

    @declared_attr
    def __tablename__(cls):
        return 'c_event'

    """
    Child table
    """
    event_id = Column(Integer, primary_key=True)
    event_type = Column(Integer, nullable=False)
    calling_party = Column(Text)
    receiving_party = Column(Text)
    hunt_group = Column(Text)
    is_conference = Column(Text)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    tag = Column(Text)
    recording_rule = Column(Integer)
    call_id = Column(Integer, ForeignKey(CallTable.call_id))

    def __json__(self):
        return list(self.__mapper__.columns.keys())

    @hybrid_property
    def length(self):
        return self.end_time - self.start_time

    def __lt__(self, other):
        # Gives EventTable a sortable property
        return self.event_id < other.event_id
