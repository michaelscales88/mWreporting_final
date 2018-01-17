# client/tasks.py
from flask import g, abort
from sqlalchemy.sql import and_
from sqlalchemy.dialects import postgresql


from app.util.tasks import query_to_frame
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


def add_client_alias(frame):
    # Show the clients as row names
    frame.insert(0, "Client", list(frame.index))
    return frame


def add_client(client_name, client_ext):
    # See if client already exists
    client = find_client(client_name, client_ext)

    if client:
        client.active = True
    else:
        new_client = Client(client_name=client_name, ext=client_ext)
        g.local_session.add(new_client)
    return True


def disable_client(client_name, client_ext):
    # See if client already exists
    client = find_client(client_name, client_ext)
    if client:
        client.active = False
    return True


def client_task(task_name, client_name=None, client_ext=None):
    if client_name and client_ext:
        if task_name == 'add':
            result = add_client(client_name, client_ext)

        elif task_name == 'remove':
            result = disable_client(client_name, client_ext)
        else:
            result = False
        status = 200 if result else 404
    elif task_name == 'get':
        result = query_to_frame(get_clients())
        status = 200
    else:
        result = False
        status = 404
        abort(status)

    return result, status
