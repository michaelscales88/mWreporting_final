# client/tasks.py
from sqlalchemy.sql import and_


from backend.services.app_tasks import query_to_frame
from .models import ClientModel


def get_clients(status=True):
    query = ClientModel.query.filter(
        ClientModel.active == status
    )
    return query_to_frame(query)


def find_client_active(client_name, client_ext, active=True):
    return ClientModel.query.filter(
        and_(
            ClientModel.client_name == client_name,
            ClientModel.ext == client_ext,
            ClientModel.active == active
        )
    ).first()


def find_client(client_name, client_ext):
    return ClientModel.query.filter(
        and_(
            ClientModel.client_name == client_name,
            ClientModel.ext == client_ext
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
