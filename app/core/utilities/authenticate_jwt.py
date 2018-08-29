# user/utilities.py
from flask_security.utils import verify_password

from ..models import UserModel


def authenticate(username, password):
    user = UserModel.query.filter(UserModel.username == username).first()
    if user and verify_password(user.password.encode('utf-8'), password.encode('utf-8')):
        return user
    else:
        raise UserWarning("Invalid security server credentials.")
