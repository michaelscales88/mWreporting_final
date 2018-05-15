# backend/__init__.py
from .factories import create_application
from backend.factories.server import create_server


def build_server(*cfg):
    """
    Creates the server that the html pages interact with.
    """
    return create_server(create_application(*cfg))
