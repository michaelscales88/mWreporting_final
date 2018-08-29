# user/views/__init__.py
import logging
from sqlalchemy.event import listens_for
from app.extensions import BaseModel
from .users import UsersView
from .roles import RolesView


logger = logging.getLogger("app.sqlalchemy")


@listens_for(BaseModel, "after_insert", propagate=True)
def after_insert_listener(mapper, connection, target):
    warn_msg = "Inserted Record: {}".format(target)
    logger.warning(warn_msg)


@listens_for(BaseModel, "after_update", propagate=True)
def after_update_listener(mapper, connection, target):
    warn_msg = "Updated Record: {}".format(target)
    logger.warning(warn_msg)


@listens_for(BaseModel, "after_delete", propagate=True)
def after_delete_listener(mapper, connection, target):
    warn_msg = "Deleted Record: {}".format(target)
    logger.warning(warn_msg)
