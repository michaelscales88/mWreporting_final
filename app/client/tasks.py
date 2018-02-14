# client/tasks.py
from sqlalchemy.sql import and_
from sqlalchemy.dialects import postgresql


from .models import ClientModel


def get_clients(active=True):
    return ClientModel.query.filter(ClientModel.active == active).all()


def find_client(client_name, client_ext, active=True):
    return ClientModel.query.filter(
        and_(
            ClientModel.client_name == client_name,
            ClientModel.ext == client_ext,
            ClientModel.active == active
        )
    ).first()


def add_client(client_name, client_ext):
    # See if client already exists
    client = find_client(client_name, client_ext)

    if client:
        client.active = True
    else:
        ClientModel.create(client_name=client_name, ext=client_ext)

    return True


def disable_client(client_name, client_ext):
    # See if client already exists
    client = find_client(client_name, client_ext)
    if client:
        client.active = False

    return True
