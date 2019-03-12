# security/__init__.py
import jwt
import logging
from functools import wraps

from flask import request, current_app, abort, url_for
from flask_admin import helpers
from flask_security import Security, SQLAlchemyUserDatastore

from modules import app
from modules.base.base_model import BaseModel
from modules.extensions import admin
from modules.utilities.forms import ExtendedLoginForm, ExtendedRegisterForm
from .models import UserModel, RolesModel

logger = logging.getLogger("app")

user_datastore = SQLAlchemyUserDatastore(BaseModel, UserModel, RolesModel)

# Manage user roles and security
security = Security(
    app, user_datastore,
    login_form=ExtendedLoginForm,
    register_form=ExtendedRegisterForm
)


@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=helpers,
        get_url=url_for
    )


# decorator for checking for token
def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', None)
        if auth_header:
            token = auth_header.split(" ")[1]
        else:
            token = ''

        if not token:
            return abort(401, 'Token is required.')

        try:
            payload = jwt.decode(token, current_app.config['SECRET_KEY'])
            kwargs['current_id'] = payload['identity']
        except jwt.InvalidTokenError as err:
            logger.warning("Aborting request: invalid token error.")
            return abort(401, err)

        return f(*args, **kwargs)

    return decorated


def user_auth(fn):
    @jwt_required
    @wraps(fn)
    def wrapper(*args, **kwargs):
        uid = kwargs.pop("current_id")
        user = UserModel.find(uid)
        if user:
            request.form['_user_id'] = user.id
            logger.warning("User accessing a resource.")
            return fn(*args, **kwargs)
        else:
            return abort(
                401,
                'Error: The user does not have permission to access this resource.'
            )

    return wrapper
