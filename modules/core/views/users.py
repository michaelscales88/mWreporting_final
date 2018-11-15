from flask import flash
from modules.base_view import BaseView
from modules.core.models import UserModel
from .forms import CustomPasswordField


class UsersView(BaseView):
    column_exclude_list = ['password']
    column_searchable_list = (
        'first_name', UserModel.first_name,
        'last_name', UserModel.last_name,
        'username', UserModel.username
    )
    form_columns = ('email', 'first_name', 'last_name', 'username', 'password', 'roles', 'active')
    form_overrides = dict(password=CustomPasswordField)
    form_widget_args = dict(
        password=dict(
            placeholder='Enter new password here to change password'
        )
    )

    def delete_model(self, model):
        if model.id == 1:
            flash("Cannot delete [ {} ] user.".format(model.name), category="warning")
            return False
        return super().delete_model(model)


