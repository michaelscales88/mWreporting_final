from celery.schedules import crontab
from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import func, and_
from sqlalchemy.dialects import postgresql
from pandas import DataFrame

from .models import Client


_mmap = {
    "client": Client
}


def get_clients():

    clients = Client.all()
    df = DataFrame.from_s
    return
