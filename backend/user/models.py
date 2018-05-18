# users/models.py
from flask_user import UserMixin
from flask_user.forms import RegisterForm, StringField

from backend.services.extensions import db, ma


class MyRegisterForm(RegisterForm):
    first_name = StringField('First name')
    last_name = StringField('Last name')


client_user_association = db.Table(
    'client_user_association', db.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('client_id', db.Integer, db.ForeignKey('client.id'))
)


class UserModel(db.Model, UserMixin):
    """ User Model for storing user related details """
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)

    # User authentication information
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, server_default='')

    # User email information
    email = db.Column(db.String(255), nullable=False, unique=True)
    confirmed_at = db.Column(db.DateTime())

    # User information
    active = db.Column('is_active', db.Boolean(), nullable=False, default=1)
    first_name = db.Column(db.String(100), nullable=False, server_default='')
    last_name = db.Column(db.String(100), nullable=False, server_default='')

    clients = db.relationship(
        "ClientModel",
        secondary=client_user_association,
        backref="users",
        cascade='all'
    )

    @classmethod
    def get(cls, uid):
        return cls.query.filter(cls.id == uid).first()


class ClientUserSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('ext', 'client_name')


_mmap = {
    "user": UserModel
}
