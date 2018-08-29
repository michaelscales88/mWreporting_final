#
from app.core import get_model_by_tablename
from app.extensions import db
from .client_model import ClientModel

user_model = get_model_by_tablename("user")

client_user_association = db.Table(
    'client_manager_association', db.metadata,
    db.Column('client_manager_id', db.Integer, db.ForeignKey('client_manager.id')),
    db.Column('client_model_id', db.Integer, db.ForeignKey('client_model.id'))
)


class ClientManager(db.Model):
    __tablename__ = 'client_manager'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    manager = db.relationship(user_model, backref="clients")

    clients = db.relationship(
        ClientModel,
        secondary=client_user_association,
        cascade='all'
    )

    def __str__(self):
        return str(self.manager)
