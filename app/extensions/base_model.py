# services/custom_db.py
from flask_sqlalchemy.model import BindMetaMixin
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_mixins import AllFeaturesMixin


# Support migrate
def migration_meta():
    return MetaData(
        naming_convention={
            "ix": 'ix_%(column_0_label)s',
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s"
        }
    )


class NoNameMeta(BindMetaMixin, DeclarativeMeta):
    """
    Custom MetaData to disable default tablename generation
    Supports bind_keys to for multiple database
    """
    pass


Base = declarative_base(metaclass=NoNameMeta, name='Model')


class BaseModel(Base, AllFeaturesMixin):
    __abstract__ = True
    pass

    @hybrid_property
    def headers(self):
        return self.__repr_attrs__
