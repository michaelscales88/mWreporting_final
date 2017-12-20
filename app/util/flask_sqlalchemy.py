from flask_sqlalchemy import BaseQuery, SQLAlchemy
from flask_sqlalchemy.model import BindMetaMixin, Model
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy_utils import generic_repr


# Support migrate
convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}


# get a Model by id, or return a default
class GetOrQuery(BaseQuery):
    def get_or(self, ident, default=None):
        return self.get(ident) or default


@generic_repr
class _Base(BindMetaMixin, DeclarativeMeta):
    """
    Custom model base to disable default tablename generation
    Supports bind_keys to for multiple database
    Adds a generic string representation
    """
    pass


Base = declarative_base(cls=Model, metaclass=_Base, name='Model')


def get_sqlalchemy(app):
    metadata = MetaData(naming_convention=convention)
    _db = SQLAlchemy(
        app, metadata=metadata,
        query_class=GetOrQuery,
        model_class=Base
    )
    _db.make_declarative_base(Base)

    return _db
