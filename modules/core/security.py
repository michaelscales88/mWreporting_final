# security/__init__.py
from flask import url_for
from flask_admin import helpers
from flask_security import Security, SQLAlchemyUserDatastore

from modules import app
from modules.extensions import admin, BaseModel
from modules.utilities.forms import ExtendedLoginForm, ExtendedRegisterForm
from .models import UserModel, RolesModel

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
