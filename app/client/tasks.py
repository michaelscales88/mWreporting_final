from celery.schedules import crontab
from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import func, and_
from sqlalchemy.dialects import postgresql

from .models import Client


_mmap = {
    "client_table": Client
}


def get_clients():
    return Client.query
