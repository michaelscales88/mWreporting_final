# user/utilities.py
from .models import UserModel
from werkzeug.security import safe_str_cmp


def authenticate(username, password):
    user = UserModel.query.filter(UserModel.username == username).first()
    if user and safe_str_cmp(user.password.encode('utf-8'), password.encode('utf-8')):
        return user
    else:
        raise UserWarning("Invalid security server credentials.")
