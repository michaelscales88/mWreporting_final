# client/tasks.py
from flask import g
from sqlalchemy.sql import and_
from sqlalchemy.dialects import postgresql

from .models import Client


_mmap = {
    "client_table": Client
}


def get_clients():
    return g.local_session.query(Client).filter(Client.active == 1)


def find_client(client_name, client_ext):
    return g.local_session.query(Client).filter(
        and_(
            Client.client_name == client_name,
            Client.ext == client_ext
        )
    ).first()


def add_client(client_name, client_ext):
    # See if client already exists
    client = find_client(client_name, client_ext)

    if client:
        client.active = True
    else:
        new_client = Client(client_name=client_name, ext=client_ext)
        g.local_session.add(new_client)


def disable_client(client_name, client_ext):
    # See if client already exists
    client = find_client(client_name, client_ext)
    if client:
        client.active = False


def client_task(task_name, client_name=None, client_ext=None):
    if client_name or client_ext:
        if task_name == 'add':
            add_client(client_name, client_ext)
        elif task_name == 'remove':
            disable_client(client_name, client_ext)
        else:
            print('Bad task_name.')
    else:
        if task_name == 'get':
            return get_clients()
