from flask_sqlalchemy import BaseQuery, SQLAlchemy
from flask_sqlalchemy.model import BindMetaMixin, Model
from sqlalchemy import MetaData
from sqlalchemy.inspection import inspect
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy_mixins import AllFeaturesMixin, ReprMixin


# Support migrate
convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}


class Base(Model, AllFeaturesMixin):
    __abstract__ = True
    __repr__ = ReprMixin.__repr__
    pass


# get a Model by id, or return a default
class GetOrQuery(BaseQuery):
    def get_or(self, ident, default=None):
        return self.get(ident) or default


class NoNameMeta(BindMetaMixin, DeclarativeMeta):
    """
    Custom MetaData to disable default tablename generation
    Supports bind_keys to for multiple database
    """
    pass


def get_sqlalchemy(app):
    metadata = MetaData(naming_convention=convention)
    _db = SQLAlchemy(
        app, metadata=metadata,
        query_class=GetOrQuery,
        model_class=declarative_base(cls=Base, metaclass=NoNameMeta, name='Model')
    )
    return _db


def get_mapped_class(obj):
    for o in obj:
        if isinstance(o.__class__, DeclarativeMeta):
            # Mapped class has meta data and fn
            return inspect(o)
    else:
        return False


def server_side_processing(
        query,  # Unmodified query object
        query_params,
        ascending=False
):
    entity = get_mapped_class(query)
    # if entity:
    #     # Find ORM mapper
    #     pk = entity.primary_key[0]
    #
    #     # Sort order
    #     query = query.order_by(pk.asc()) if ascending else query.order_by(pk.desc())

    # Offset if we are going beyond the initial ROWS_PER_PAGE
    if query_params['start'] > 0:
        query = query.offset(query_params['start'])

    # Limit the number of rows to the page
    query = query.limit(query_params['length'])

    return query
