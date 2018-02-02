# services/custom_db.py
from flask_sqlalchemy.model import BindMetaMixin
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import sessionmaker
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


def abort_ro(*args,**kwargs):
    """
    Avoid writing to ro session
    """
    print("Writing operations disabled. Aborting session flush.")
    return


def get_session(engine, echo=False, readonly=False):
    engine = create_engine(engine, echo=echo)
    session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    if readonly:
        session.flush = abort_ro  # Disable flushing to db
    return session()
