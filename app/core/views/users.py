from app.base_view import BaseView
from ..models import UserModel


class UsersView(BaseView):
    column_exclude_list = ['password']
    column_searchable_list = (
        'first_name', UserModel.first_name,
        'last_name', UserModel.last_name,
        'username', UserModel.username
    )
    form_columns = ('email', 'first_name', 'last_name', 'username', 'password', 'roles', 'active')
    form_widget_args = {
        'password': {
            'style': 'color: red',
            'minlength': '8'
        }
    }
