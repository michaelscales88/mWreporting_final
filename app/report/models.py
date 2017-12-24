from app import app, db

from app.database import get_scoped_session
from app.util import json_type
from app.util.base_models import GetOrQuery


app_meta_session = get_scoped_session(app, db, 'app_meta')


class SLAReport(db.Model):

    __bind_key__ = 'app_meta'
    __tablename__ = 'sla_report'
    __repr_attrs__ = ['id', 'start_time', 'end_time', 'report', 'notes']
    query = app_meta_session.query_property(query_cls=GetOrQuery)

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    report = db.Column(json_type)
    notes = db.Column(db.Text)
