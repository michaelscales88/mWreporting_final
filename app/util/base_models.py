from flask_sqlalchemy.model import BindMetaMixin, Model
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy_mixins import AllFeaturesMixin, ReprMixin


# Support migrate
convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}


class ModelBase(Model, AllFeaturesMixin):
    __abstract__ = True
    __repr__ = ReprMixin.__repr__
    pass


class NoNameMeta(BindMetaMixin, DeclarativeMeta):
    """
    Custom MetaData to disable default tablename generation
    Supports bind_keys to for multiple database
    """
    pass
